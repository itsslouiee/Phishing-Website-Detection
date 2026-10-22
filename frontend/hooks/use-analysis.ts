'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { compareUrl, predictUrl } from '@/lib/api'
import { toErrorState, type AsyncState } from '@/lib/async'
import type { CompareResponse, PredictResponse } from '@/lib/schemas'

/**
 * Orchestrates one URL analysis:
 *  - POST /api/v1/predict  → XGBoost result for the main section
 *  - POST /api/v1/compare  → all three models for the comparison section
 *
 * Both requests start together and settle independently, so the main result
 * appears as soon as it is ready and a failure in one never hides the other.
 * Starting a new analysis cancels anything still in flight, so results from an
 * older URL can never overwrite newer ones.
 */
export function useAnalysis() {
  const [url, setUrl] = useState<string | null>(null)
  const [predict, setPredict] = useState<AsyncState<PredictResponse>>({ status: 'idle' })
  const [compare, setCompare] = useState<AsyncState<CompareResponse>>({ status: 'idle' })

  const urlRef = useRef<string | null>(null)
  const predictController = useRef<AbortController | null>(null)
  const compareController = useRef<AbortController | null>(null)

  const runPredict = useCallback((target: string) => {
    predictController.current?.abort()
    const controller = new AbortController()
    predictController.current = controller
    setPredict({ status: 'loading' })
    predictUrl(target, controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setPredict({ status: 'success', data })
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) setPredict(toErrorState(error))
      })
  }, [])

  const runCompare = useCallback((target: string) => {
    compareController.current?.abort()
    const controller = new AbortController()
    compareController.current = controller
    setCompare({ status: 'loading' })
    compareUrl(target, controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setCompare({ status: 'success', data })
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) setCompare(toErrorState(error))
      })
  }, [])

  const analyze = useCallback(
    (target: string) => {
      urlRef.current = target
      setUrl(target)
      runPredict(target)
      runCompare(target)
    },
    [runPredict, runCompare],
  )

  const retryPredict = useCallback(() => {
    if (urlRef.current) runPredict(urlRef.current)
  }, [runPredict])

  const retryCompare = useCallback(() => {
    if (urlRef.current) runCompare(urlRef.current)
  }, [runCompare])

  useEffect(() => {
    return () => {
      predictController.current?.abort()
      compareController.current?.abort()
    }
  }, [])

  return { url, predict, compare, analyze, retryPredict, retryCompare }
}
