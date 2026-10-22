import { CircleAlert, CircleCheck, Link2, ShieldCheck, TriangleAlert } from 'lucide-react'
import type { AsyncState } from '@/lib/async'
import { formatPercent } from '@/lib/format'
import { MODEL_IDS, MODEL_META, PRIMARY_MODEL, type ModelId } from '@/lib/models'
import type { CompareResponse, Prediction } from '@/lib/schemas'
import { cn } from '@/lib/utils'
import { ErrorNotice } from './error-notice'

type CardState = { kind: 'idle' } | { kind: 'loading' } | { kind: 'ready'; prediction: Prediction }

function ProbabilityBar({ value, phishing }: { value: number; phishing: boolean }) {
  return (
    <div>
      <div className="flex items-baseline justify-between text-xs">
        <span className="text-ink-2">Phishing probability</span>
        <span className="font-mono text-base font-semibold tabular-nums text-ink">{formatPercent(value)}</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-line/60" role="presentation">
        <div
          className={cn('h-full origin-left animate-grow rounded-full', phishing ? 'bg-danger' : 'bg-safe')}
          style={{ width: `${Math.max(value * 100, 1)}%` }}
        />
      </div>
    </div>
  )
}

function ModelPredictionCard({ id, state }: { id: ModelId; state: CardState }) {
  const meta = MODEL_META[id]
  const prediction = state.kind === 'ready' ? state.prediction : null
  const phishing = prediction?.label === 'phishing'
  const probability = prediction?.phishing_probability ?? null

  return (
    <article className="flex min-h-[200px] flex-col rounded-2xl border border-line bg-surface-2/80 p-5 transition-colors hover:border-violet/40">
      <header className="flex items-center justify-between gap-3">
        <h4 className="flex items-center gap-2 text-sm font-semibold text-ink">
          <span className="size-2.5 rounded-full" style={{ background: meta.color }} aria-hidden="true" />
          {meta.name}
        </h4>
        {id === PRIMARY_MODEL && (
          <span className="rounded-full border border-violet/25 bg-violet/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-lilac">
            Primary
          </span>
        )}
      </header>

      {state.kind === 'idle' && (
        <div className="mt-auto pt-8">
          <p className="font-mono text-3xl text-ink-3" aria-hidden="true">
            —
          </p>
          <p className="mt-2 text-xs text-ink-3">Waiting for a URL</p>
        </div>
      )}

      {state.kind === 'loading' && (
        <div className="mt-auto space-y-3 pt-8" aria-hidden="true">
          <div className="h-8 w-32 animate-pulse rounded-lg bg-line/60" />
          <div className="h-2 w-full animate-pulse rounded-full bg-line/40" />
        </div>
      )}

      {prediction && (
        <div className="mt-auto animate-rise space-y-5 pt-6">
          <p
            className={cn(
              'inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-semibold',
              phishing ? 'border-danger/25 bg-danger/10 text-danger' : 'border-safe/25 bg-safe/10 text-safe',
            )}
          >
            {phishing ? <TriangleAlert className="size-4" aria-hidden="true" /> : <ShieldCheck className="size-4" aria-hidden="true" />}
            {phishing ? 'Phishing' : 'Legitimate'}
          </p>
          {probability !== null ? (
            <ProbabilityBar value={probability} phishing={phishing} />
          ) : (
            <p className="text-xs text-ink-3">No probability provided for this model.</p>
          )}
        </div>
      )}
    </article>
  )
}

function Consensus({ predictions }: { predictions: Prediction[] }) {
  const phishingCount = predictions.filter((p) => p.label === 'phishing').length
  const total = predictions.length
  const unanimous = phishingCount === 0 || phishingCount === total

  return (
    <p
      className={cn(
        'mb-4 flex items-start gap-2.5 rounded-xl border px-4 py-3 text-sm',
        unanimous ? 'border-line bg-surface-2/60 text-ink-2' : 'border-pink/30 bg-pink/[0.07] text-ink',
      )}
    >
      {unanimous ? (
        <CircleCheck className="mt-0.5 size-4 shrink-0 text-lilac" aria-hidden="true" />
      ) : (
        <CircleAlert className="mt-0.5 size-4 shrink-0 text-pink" aria-hidden="true" />
      )}
      {unanimous ? (
        <span>
          All {total} models agree: <strong className="font-semibold text-ink">{phishingCount === 0 ? 'legitimate' : 'phishing'}</strong>.
        </span>
      ) : (
        <span>
          <strong className="font-semibold">The models disagree.</strong> {phishingCount} of {total} classify this URL as phishing;{' '}
          {total - phishingCount} as legitimate.
        </span>
      )}
    </p>
  )
}

export function UrlPredictions({
  url,
  state,
  onRetry,
}: {
  url: string | null
  state: AsyncState<CompareResponse>
  onRetry: () => void
}) {
  if (state.status === 'error') {
    return <ErrorNotice title="Couldn't compare the models for this URL" message={state.message} onRetry={onRetry} />
  }

  const predictions = state.status === 'success' ? state.data.predictions : null

  return (
    <div aria-live="polite">
      {url ? (
        <p className="mb-4 flex min-w-0 items-center gap-2 text-xs text-ink-3">
          <Link2 className="size-3.5 shrink-0" aria-hidden="true" />
          <span className="shrink-0">Analyzed URL</span>
          <span className="min-w-0 truncate font-mono text-ink-2" title={url}>
            {url}
          </span>
        </p>
      ) : (
        <p className="mb-4 text-sm text-ink-2">
          Analyze a URL above and each model&apos;s prediction for it appears here automatically.
        </p>
      )}

      {predictions && <Consensus predictions={predictions} />}

      <div className="grid gap-4 md:grid-cols-3">
        {MODEL_IDS.map((id) => {
          const prediction = predictions?.find((p) => p.model === id)
          const cardState: CardState = prediction
            ? { kind: 'ready', prediction }
            : state.status === 'loading'
              ? { kind: 'loading' }
              : { kind: 'idle' }
          return <ModelPredictionCard key={id} id={id} state={cardState} />
        })}
      </div>
    </div>
  )
}
