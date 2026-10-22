import { ArrowDown, LoaderCircle, ShieldCheck, TriangleAlert } from 'lucide-react'
import type { AsyncState } from '@/lib/async'
import { MODEL_META } from '@/lib/models'
import type { PredictResponse } from '@/lib/schemas'
import { cn } from '@/lib/utils'
import { ErrorNotice } from './error-notice'
import { ProbabilityArc } from './probability-arc'

function AnalyzingCard() {
  return (
    <div className="relative animate-rise overflow-hidden rounded-3xl border border-line bg-surface/70 p-6 sm:p-8">
      <div className="absolute inset-x-0 top-0 h-px overflow-hidden" aria-hidden="true">
        <div className="h-full w-1/4 animate-scan bg-gradient-to-r from-transparent via-lilac to-transparent" />
      </div>
      <div className="flex items-center gap-4">
        <div className="grid size-14 place-items-center rounded-2xl bg-violet/10 text-lilac">
          <LoaderCircle className="size-7 animate-spin" aria-hidden="true" />
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.14em] text-ink-3">XGBoost</p>
          <p className="mt-1 text-2xl font-semibold tracking-tight text-ink">Analyzing URL…</p>
        </div>
      </div>
      <div className="mt-8 space-y-3" aria-hidden="true">
        <div className="h-3 w-2/3 animate-pulse rounded-full bg-line/60" />
        <div className="h-3 w-1/2 animate-pulse rounded-full bg-line/40" />
      </div>
    </div>
  )
}

function VerdictCard({ result, url }: { result: PredictResponse; url: string | null }) {
  const phishing = result.label === 'phishing'
  const probability = result.phishing_probability ?? null
  const tone = phishing ? 'danger' : 'safe'

  return (
    <section
      aria-label="XGBoost prediction"
      className={cn(
        'animate-rise rounded-3xl border p-6 sm:p-8',
        phishing
          ? 'border-danger/30 bg-gradient-to-br from-danger/[0.09] to-surface/60'
          : 'border-safe/30 bg-gradient-to-br from-safe/[0.08] to-surface/60',
      )}
    >
      <div className="flex flex-col gap-8 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <p className="flex items-center gap-2 text-xs font-medium text-ink-2">
            <span className="size-2 rounded-full" style={{ background: MODEL_META.xgboost.color }} aria-hidden="true" />
            XGBoost <span className="text-ink-3">· primary model</span>
          </p>

          <div className="mt-5 flex items-center gap-4">
            <div
              className={cn(
                'grid size-14 shrink-0 place-items-center rounded-2xl',
                phishing ? 'bg-danger/15 text-danger' : 'bg-safe/15 text-safe',
              )}
            >
              {phishing ? <TriangleAlert className="size-7" aria-hidden="true" /> : <ShieldCheck className="size-7" aria-hidden="true" />}
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.14em] text-ink-3">Prediction</p>
              <h3 className="mt-1 text-3xl font-semibold tracking-[-0.03em] text-ink sm:text-4xl">
                {phishing ? 'Likely phishing' : 'Likely legitimate'}
              </h3>
            </div>
          </div>

          <p className="mt-7 text-xs uppercase tracking-[0.14em] text-ink-3">Analyzed URL</p>
          <p className="mt-1.5 break-all rounded-xl border border-line bg-bg/60 px-3 py-2 font-mono text-xs leading-5 text-ink-2">
            {url ?? result.url}
          </p>
        </div>

        {probability !== null && (
          <div className="flex justify-center md:w-[260px] md:shrink-0">
            <ProbabilityArc value={probability} tone={tone} />
          </div>
        )}
      </div>

      {probability === null && (
        <p className="mt-5 text-xs text-ink-3">The backend did not provide a probability for this prediction.</p>
      )}

      <p className="mt-7 flex items-center gap-2 border-t border-line/70 pt-4 text-xs text-ink-3">
        <ArrowDown className="size-3.5 shrink-0 animate-nudge" aria-hidden="true" />
        Scroll down to see how Random Forest and Logistic Regression classified this same URL.
      </p>
    </section>
  )
}

export function ResultPanel({
  state,
  url,
  onRetry,
}: {
  state: AsyncState<PredictResponse>
  url: string | null
  onRetry: () => void
}) {
  return (
    <div aria-live="polite" className="mt-6">
      {state.status === 'loading' && <AnalyzingCard />}
      {state.status === 'error' && (
        <ErrorNotice title="Couldn't analyze this URL" message={state.message} onRetry={onRetry} />
      )}
      {state.status === 'success' && <VerdictCard result={state.data} url={url} />}
    </div>
  )
}
