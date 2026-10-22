'use client'

import { useCallback, useEffect, useState } from 'react'
import { toErrorState, type AsyncState } from '@/lib/async'

/**
 * Loads a resource once on mount, with a retry action.
 * `fetcher` must be a stable (module-level) function.
 */
export function useApiResource<T>(fetcher: (signal: AbortSignal) => Promise<T>) {
  const [state, setState] = useState<AsyncState<T>>({ status: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    fetcher(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setState({ status: 'success', data })
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) setState(toErrorState(error))
      })
    return () => controller.abort()
  }, [fetcher, attempt])

  const retry = useCallback(() => {
    setState({ status: 'loading' })
    setAttempt((value) => value + 1)
  }, [])

  return { state, retry }
}
