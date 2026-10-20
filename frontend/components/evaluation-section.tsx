import { BarChart3 } from 'lucide-react'
import { BEST_MODEL, EVALUATION_RESULTS, type EvaluationMetrics } from '@/lib/config'

const METRICS: { key: keyof EvaluationMetrics; label: string; hint: string }[] = [
  { key: 'accuracy', label: 'Accuracy', hint: 'Share of all predictions that were correct' },
  { key: 'precision', label: 'Precision', hint: 'Of URLs flagged as phishing, how many were' },
  { key: 'recall', label: 'Recall', hint: 'Of actual phishing URLs, how many were caught' },
  { key: 'f1', label: 'F1-score', hint: 'Balance between precision and recall' },
]

const pct = (v?: number) => (v == null ? '—' : `${(v * 100).toFixed(1)}%`)

function MetricCard({ label, hint, value }: { label: string; hint: string; value?: number }) {
  const has = value != null
  return (
    <div className="rounded-xl border border-white/[0.06] bg-[#0b1020] p-4 transition-colors hover:border-violet-400/25">
      <p className="text-xs font-medium text-[#c5cee0]">{label}</p>
      <p className={`mt-3 font-mono text-2xl tabular-nums ${has ? 'text-[#e8edfa]' : 'text-[#475569]'}`}>{pct(value)}</p>
      {has && (
        <div className="mt-3 h-1 overflow-hidden rounded-full bg-[#1b2740]" aria-hidden>
          <div className="h-full rounded-full bg-violet-400" style={{ width: `${Math.min(100, Math.max(0, value * 100))}%` }} />
        </div>
      )}
      <p className="mt-3 text-[11px] leading-4 text-[#64748b]">{has ? hint : 'Awaiting data'}</p>
    </div>
  )
}

export function EvaluationSection() {
  const results = EVALUATION_RESULTS
  const entries = results.length ? results : [null]

  return (
    <section id="evaluation" aria-labelledby="evaluation-title" className="relative mx-auto max-w-5xl scroll-mt-6 px-5 pb-16 lg:px-8">
      <div className="rounded-2xl border border-[#293650] bg-[#111a2e]/60 p-5 sm:p-8">
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-violet-300">Model evaluation</p>
            <h2 id="evaluation-title" className="mt-2 text-2xl font-semibold tracking-[-0.03em]">How the models perform</h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-[#64748b]">
              {results.length
                ? 'Metrics measured on held-out test data. They describe this evaluation only, not real-world effectiveness.'
                : 'Verified evaluation metrics will appear here once available. No placeholder numbers, no inflated claims.'}
            </p>
          </div>
          <div className="hidden rounded-xl border border-violet-400/20 bg-violet-400/10 p-3 text-violet-200 sm:block"><BarChart3 className="size-5" aria-hidden /></div>
        </div>

        <div className="mt-7 space-y-6">
          {entries.map((entry) => (
            <div key={entry?.modelId ?? 'pending'}>
              {entry && (
                <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1">
                  <h3 className="text-sm font-medium text-[#e8edfa]">{entry.modelLabel}</h3>
                  {BEST_MODEL?.id === entry.modelId && (
                    <span className="rounded-full border border-violet-400/25 bg-violet-400/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-violet-200">Default · best model</span>
                  )}
                  {entry.dataset && <span className="text-xs text-[#64748b]">{entry.dataset}</span>}
                </div>
              )}
              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                {METRICS.map((m) => <MetricCard key={m.key} label={m.label} hint={m.hint} value={entry?.metrics[m.key]} />)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
