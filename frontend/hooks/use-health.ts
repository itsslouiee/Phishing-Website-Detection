'use client'

import { useEffect, useState } from 'react'
import { getHealth } from '@/lib/api'
import { toErrorState, type AsyncState } from '@/lib/async'
import type { Health } from '@/lib/schemas'

const POLL_INTERVAL_MS = 30_000

/** Checks GET /health on mount and then periodically, without flashing a loading state. */
export function useHealth(): AsyncState<Health> {
  const [state, setState] = useState<AsyncState<Health>>({ status: 'loading' })

  useEffect(() => {
    const controller = new AbortController()
    let timer: ReturnType<typeof setTimeout> | undefined

    async function check() {
      try {
        const data = await getHealth(controller.signal)
        if (!controller.signal.aborted) setState({ status: 'success', data })
      } catch (error) {
        if (!controller.signal.aborted) setState(toErrorState(error))
      }
      if (!controller.signal.aborted) timer = setTimeout(check, POLL_INTERVAL_MS)
    }

    void check()
    return () => {
      controller.abort()
      clearTimeout(timer)
    }
  }, [])

  return state
}
