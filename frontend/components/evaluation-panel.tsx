import { Trophy } from 'lucide-react'
import type { AsyncState } from '@/lib/async'
import { formatCount, formatPercent } from '@/lib/format'
import { MODEL_IDS, MODEL_META, type ModelId } from '@/lib/models'
import type { ConfusionMatrixData, EvaluationResponse, ModelEvaluation } from '@/lib/schemas'
import { ErrorNotice } from './error-notice'

type EvaluationById = Partial<Record<ModelId, ModelEvaluation>>
type MetricKey = keyof ModelEvaluation['metrics']

const METRICS: { key: MetricKey; label: string; hint: string }[] = [
  { key: 'accuracy', label: 'Accuracy', hint: 'Share of all URLs classified correctly' },
  { key: 'precision', label: 'Precision', hint: 'Of URLs flagged as phishing, how many truly were' },
  { key: 'recall', label: 'Recall', hint: 'Of all phishing URLs, how many were caught' },
  { key: 'f1', label: 'F1-score', hint: 'Balance between precision and recall' },
  { key: 'roc_auc', label: 'ROC-AUC', hint: 'How well phishing is ranked above legitimate' },
]

function Legend() {
  return (
    <ul className="mb-2 flex flex-wrap gap-x-6 gap-y-2 text-xs text-ink-2">
      {MODEL_IDS.map((id) => (
        <li key={id} className="flex items-center gap-2">
          <span className="size-2.5 rounded-full" style={{ background: MODEL_META[id].color }} aria-hidden="true" />
          {MODEL_META[id].name}
        </li>
      ))}
    </ul>
  )
}

function MetricsComparison({ byId }: { byId: EvaluationById }) {
  const rows = METRICS.map((metric) => ({
    ...metric,
    values: MODEL_IDS.map((id) => byId[id]?.metrics[metric.key] ?? null),
  })).filter((row) => row.values.some((value) => value !== null))

  if (rows.length === 0) {
    return <p className="text-sm text-ink-2">The backend did not provide any metrics.</p>
  }

  return (
    <div>
      <Legend />
      {rows.map((row) => {
        const present = row.values.filter((value): value is number => value !== null)
        const best = present.length > 1 ? Math.max(...present) : null
        return (
          <div key={row.key} className="grid gap-3 border-t border-line/70 py-5 first:border-t-0 md:grid-cols-[210px_1fr] md:gap-8">
            <div>
              <p className="text-sm font-semibold text-ink">{row.label}</p>
              <p className="mt-0.5 text-xs leading-5 text-ink-3">{row.hint}</p>
            </div>
            <div className="space-y-2.5">
              {MODEL_IDS.map((id, index) => {
                const value = row.values[index]
                const isBest = value !== null && best !== null && Math.abs(value - best) < 1e-9
                return (
                  <div key={id} className="flex items-center gap-3">
                    <abbr title={MODEL_META[id].name} className="w-7 font-mono text-[11px] text-ink-3 no-underline">
                      {MODEL_META[id].abbr}
                    </abbr>
                    <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-line/50">
                      {value !== null && (
                        <div
                          className="h-full origin-left animate-grow rounded-full"
                          style={{ width: `${Math.max(value * 100, 0.5)}%`, background: MODEL_META[id].color }}
                        />
                      )}
                    </div>
                    <span className={`flex w-[4.75rem] items-center justify-end gap-1 font-mono text-xs tabular-nums ${isBest ? 'font-semibold text-ink' : 'text-ink-2'}`}>
                      {isBest && <Trophy className="size-3 text-lilac" aria-label="Best in this row" />}
                      {value === null ? 'n/a' : formatPercent(value, 2)}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function MatrixCell({
  value,
  rowTotal,
  label,
  correct,
  color,
}: {
  value: number
  rowTotal: number
  label: string
  correct: boolean
  color: string
}) {
  const share = rowTotal > 0 ? value / rowTotal : 0
  const background = correct
    ? `color-mix(in srgb, ${color} ${Math.round(10 + share * 45)}%, transparent)`
    : `color-mix(in srgb, var(--color-danger) ${Math.round(share * 70)}%, transparent)`
  return (
    <div className="rounded-lg border border-line/60 px-2 py-3 text-center" style={{ background }} title={`${formatPercent(share)} of this row`}>
      <p className="font-mono text-lg font-semibold tabular-nums text-ink">{formatCount(value)}</p>
      <p className="mt-0.5 text-[10px] text-ink-2">{label}</p>
    </div>
  )
}

function ConfusionMatrix({ id, matrix }: { id: ModelId; matrix: ConfusionMatrixData | null | undefined }) {
  const meta = MODEL_META[id]
  return (
    <figure className="rounded-2xl border border-line bg-surface-2/80 p-4">
      <figcaption className="mb-3 flex items-center gap-2 text-sm font-semibold text-ink">
        <span className="size-2.5 rounded-full" style={{ background: meta.color }} aria-hidden="true" />
        {meta.name}
      </figcaption>
      {matrix ? (
        <div className="grid grid-cols-[auto_1fr_1fr] items-stretch gap-1.5 text-[10px] text-ink-3">
          <div className="self-end pb-1 leading-tight">
            Actual ↓<br />
            Predicted →
          </div>
          <div className="self-end pb-1 text-center">Legitimate</div>
          <div className="self-end pb-1 text-center">Phishing</div>

          <div className="flex items-center pr-1">Legitimate</div>
          <MatrixCell value={matrix.tn} rowTotal={matrix.tn + matrix.fp} label="True negative" correct color={meta.color} />
          <MatrixCell value={matrix.fp} rowTotal={matrix.tn + matrix.fp} label="False positive" correct={false} color={meta.color} />

          <div className="flex items-center pr-1">Phishing</div>
          <MatrixCell value={matrix.fn} rowTotal={matrix.fn + matrix.tp} label="False negative" correct={false} color={meta.color} />
          <MatrixCell value={matrix.tp} rowTotal={matrix.fn + matrix.tp} label="True positive" correct color={meta.color} />
        </div>
      ) : (
        <p className="py-8 text-center text-xs text-ink-3">Confusion matrix not provided.</p>
      )}
    </figure>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-5" aria-hidden="true">
      {[0, 1, 2, 3].map((row) => (
        <div key={row} className="grid gap-3 md:grid-cols-[210px_1fr] md:gap-8">
          <div className="h-5 w-24 animate-pulse rounded-full bg-line/50" />
          <div className="space-y-2.5">
            {[0, 1, 2].map((bar) => (
              <div key={bar} className="h-2.5 animate-pulse rounded-full bg-line/40" style={{ width: `${88 - bar * 6}%` }} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export function EvaluationPanel({ state, onRetry }: { state: AsyncState<EvaluationResponse>; onRetry: () => void }) {
  if (state.status === 'loading' || state.status === 'idle') return <LoadingSkeleton />
  if (state.status === 'error') {
    return <ErrorNotice title="Couldn't load the evaluation metrics" message={state.message} onRetry={onRetry} />
  }

  const byId: EvaluationById = {}
  for (const entry of state.data.models) byId[entry.model] = entry
  const samples = state.data.evaluation_samples ?? null

  return (
    <div>
      {samples !== null && (
        <p className="mb-5 text-xs text-ink-3">
          Evaluated on <span className="font-mono text-ink-2">{formatCount(samples)}</span> samples.
        </p>
      )}
      <MetricsComparison byId={byId} />

      <div className="mt-8 border-t border-line/70 pt-6">
        <h4 className="text-sm font-semibold text-ink">Confusion matrices</h4>
        <p className="mt-1 text-xs leading-5 text-ink-3">
          Rows are the actual class, columns are the predicted class. Phishing is the positive class.
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {MODEL_IDS.map((id) => (
            <ConfusionMatrix key={id} id={id} matrix={byId[id]?.confusion_matrix} />
          ))}
        </div>
      </div>
    </div>
  )
}
