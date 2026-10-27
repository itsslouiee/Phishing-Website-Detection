'use client'

import { useState, type FormEvent } from 'react'
import { ArrowRight, CircleAlert, Link2, LoaderCircle } from 'lucide-react'
import type { AsyncState } from '@/lib/async'
import { MODEL_IDS } from '@/lib/models'
import type { Health, PredictResponse } from '@/lib/schemas'
import { validateUrl } from '@/lib/url'
import { cn } from '@/lib/utils'
import { ResultPanel } from './result-panel'
import { Button } from './ui/button'

function BackendStatus({ state }: { state: AsyncState<Health> }) {
  let dot = 'bg-ink-3'
  let text = 'Checking backend…'

  if (state.status === 'success') {
    const ready = MODEL_IDS.filter((id) => state.data.models[id]).length
    const allReady = ready === MODEL_IDS.length && state.data.status === 'ok'
    dot = allReady ? 'bg-safe' : 'bg-pink'
    text = `Backend online · ${ready} of ${MODEL_IDS.length} models ready`
  } else if (state.status === 'error') {
    dot = 'bg-danger'
    text = state.kind === 'config' ? 'API address not configured' : 'Starting detection engine...'
  }

  return (
    <p role="status" title={state.status === 'error' ? state.message : undefined} className="mt-6 flex items-center justify-center gap-2 text-xs text-ink-3">
      <span className={cn('size-1.5 rounded-full', dot)} aria-hidden="true" />
      {text}
    </p>
  )
}

export function UrlAnalyzer({
  url,
  predict,
  health,
  onAnalyze,
  onRetry,
}: {
  url: string | null
  predict: AsyncState<PredictResponse>
  health: AsyncState<Health>
  onAnalyze: (url: string) => void
  onRetry: () => void
}) {
  const [value, setValue] = useState('')
  const [error, setError] = useState<string | null>(null)
  const busy = predict.status === 'loading'

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy) return
    const result = validateUrl(value)
    if (!result.ok) {
      setError(result.message)
      return
    }
    setError(null)
    onAnalyze(result.url)
  }

  return (
    <section id="analyze" aria-labelledby="analyze-title" className="hero-grid px-5 pb-20 pt-16 sm:pb-28 sm:pt-24 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-violet/25 bg-violet/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-lilac">
            <span className="size-1.5 rounded-full bg-current" aria-hidden="true" />
            Machine learning · Security
          </span>
          <h1 id="analyze-title" className="mt-7 text-balance text-5xl font-semibold tracking-[-0.045em] sm:text-7xl">
            Know before
            <br />
            <span className="bg-gradient-to-r from-ink via-lilac to-violet bg-clip-text text-transparent">you click.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-pretty text-base leading-7 text-ink-2">
            Paste a link and see whether a trained model thinks it looks like phishing.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          noValidate
          className="mt-12 rounded-3xl border border-line bg-surface/80 p-2 shadow-[0_24px_80px_rgba(0,0,0,0.35)]"
        >
          <div className="rounded-[20px] border border-white/[0.05] bg-bg/70 p-4 sm:p-5">
            <label htmlFor="url-input" className="text-sm font-medium text-ink">
              URL to analyze
            </label>
            <div className="mt-3 flex flex-col gap-2 sm:flex-row">
              <div className="relative flex-1">
                <Link2 className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-ink-3" aria-hidden="true" />
                <input
                  id="url-input"
                  type="text"
                  inputMode="url"
                  autoComplete="off"
                  autoCapitalize="none"
                  spellCheck={false}
                  value={value}
                  onChange={(event) => setValue(event.target.value)}
                  placeholder="https://example.com"
                  aria-invalid={error ? true : undefined}
                  aria-describedby={error ? 'url-error' : undefined}
                  className="h-12 w-full rounded-xl border border-line bg-surface pl-11 pr-4 font-mono text-sm text-ink outline-none transition-colors placeholder:text-ink-3 focus:border-violet focus:ring-2 focus:ring-violet/20 aria-[invalid=true]:border-danger/60"
                />
              </div>
              <Button type="submit" disabled={busy} className="h-12 sm:w-40">
                {busy ? (
                  <>
                    <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
                    Analyzing…
                  </>
                ) : (
                  <>
                    Analyze URL
                    <ArrowRight className="size-4" aria-hidden="true" />
                  </>
                )}
              </Button>
            </div>
            {error && (
              <p id="url-error" role="alert" className="mt-3 flex items-center gap-2 text-xs text-danger">
                <CircleAlert className="size-3.5 shrink-0" aria-hidden="true" />
                {error}
              </p>
            )}
          </div>
        </form>

        <ResultPanel state={predict} url={url} onRetry={onRetry} />
        <BackendStatus state={health} />
      </div>
    </section>
  )
}
