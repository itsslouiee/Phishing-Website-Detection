'use client'

import { useEffect, useMemo, useState } from 'react'
import { BarChart3 } from 'lucide-react'
import { useModelSelection } from '@/components/model-selection-provider'
import { getEvaluationMetrics, type BackendEvaluationEntry, type BackendEvaluationResponse } from '@/lib/api'
import type { EvaluationMetrics } from '@/lib/config'

const METRICS: { key: keyof EvaluationMetrics; label: string; hint: string }[] = [
  { key: 'accuracy', label: 'Accuracy', hint: 'Share of all predictions that were correct' },
  { key: 'precision', label: 'Precision', hint: 'Of URLs flagged as phishing, how many were actually phishing' },
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
      <p className="mt-3 text-[11px] leading-4 text-[#64748b]">{hint}</p>
    </div>
  )
}

const BestBadge = () => (
  <span className="rounded-full border border-violet-400/25 bg-violet-400/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-violet-200">Best model</span>
)

export function EvaluationSection() {
  // Same state the analyzer uses, so the evaluation can never drift from the model that live prediction uses.
  const { mode, activeModelId, availableModels, loading: selectionLoading } = useModelSelection()
  const [evaluation, setEvaluation] = useState<BackendEvaluationResponse | null>(null)
  const [view, setView] = useState<'selected' | 'compare'>('selected')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const data = await getEvaluationMetrics()
        if (active) setEvaluation(data)
      } catch {
        if (active) setError('Unable to load evaluation metrics from the backend.')
      } finally {
        if (active) setLoading(false)
      }
    }

    load()
    return () => {
      active = false
    }
  }, [])

  const entries = useMemo<BackendEvaluationEntry[]>(() => evaluation?.models ?? [], [evaluation])

  // Exact id match only. No fallback to entries[0]: showing another model's numbers would be wrong.
  const selectedEntry = useMemo(() => entries.find((entry) => entry.model.id === activeModelId) ?? null, [entries, activeModelId])
  const activeLabel = availableModels.find((option) => option.id === activeModelId)?.label ?? activeModelId

  const topValues = useMemo(() => {
    const top: Partial<Record<keyof EvaluationMetrics, number>> = {}
    for (const metric of METRICS) top[metric.key] = Math.max(...entries.map((entry) => entry[metric.key]))
    return top
  }, [entries])

  const missing = availableModels.filter((option) => !entries.some((entry) => entry.model.id === option.id))

  const description = entries.length
    ? `${evaluation?.method ?? 'Evaluation'}. ${evaluation?.note ?? ''} These are not live prediction confidence scores.`
    : loading
      ? 'Loading evaluation metrics from the backend…'
      : error
        ? error
        : 'Verified evaluation metrics will appear here once available. No placeholder numbers, no inflated claims.'

  function renderSelected() {
    if (selectionLoading) return <p className="text-sm text-[#64748b]">Loading selected model…</p>
    if (!activeModelId) {
      return <p className="text-sm text-[#64748b]">The backend has not identified a best model, so there is nothing to show yet. Choose a model to see its evaluation.</p>
    }
    if (!selectedEntry) {
      return <p className="text-sm text-[#64748b]">The backend returned no evaluation metrics for {activeLabel}.</p>
    }
    return (
      <div>
        <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1">
          <h3 className="text-sm font-medium text-[#e8edfa]">{selectedEntry.model.name}</h3>
          {mode === 'best' && <span className="text-xs text-[#64748b]">Selected as Best Model</span>}
          {selectedEntry.is_default && <BestBadge />}
        </div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {METRICS.map((metric) => (
            <MetricCard key={metric.key} label={metric.label} hint={metric.hint} value={selectedEntry[metric.key]} />
          ))}
        </div>
      </div>
    )
  }

  function renderCompare() {
    return (
      <div>
        <div className="overflow-x-auto rounded-xl border border-white/[0.06] bg-[#0b1020]">
          <table className="w-full min-w-[34rem] text-left text-sm">
            <caption className="sr-only">Evaluation metrics for every model</caption>
            <thead>
              <tr className="border-b border-white/[0.06] text-xs text-[#94a3b8]">
                <th scope="col" className="px-4 py-3 font-medium">Model</th>
                {METRICS.map((metric) => (
                  <th key={metric.key} scope="col" className="px-4 py-3 text-right font-medium">{metric.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.model.id} className="border-b border-white/[0.04] last:border-0">
                  <th scope="row" className="px-4 py-3.5 font-medium text-[#e8edfa]">
                    <span className="flex flex-wrap items-center gap-2">{entry.model.name}{entry.is_default && <BestBadge />}</span>
                  </th>
                  {METRICS.map((metric) => {
                    const top = entries.length > 1 && entry[metric.key] === topValues[metric.key]
                    return (
                      <td key={metric.key} className={`px-4 py-3.5 text-right font-mono tabular-nums ${top ? 'font-semibold text-violet-200' : 'text-[#c5cee0]'}`}>
                        {pct(entry[metric.key])}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-[11px] leading-4 text-[#64748b]">
          Highest value in each column is highlighted.
          {missing.length > 0 && ` No evaluation metrics were returned for ${missing.map((option) => option.label).join(', ')}.`}
        </p>
      </div>
    )
  }

  return (
    <section id="evaluation" aria-labelledby="evaluation-title" className="relative mx-auto max-w-5xl scroll-mt-6 px-5 pb-16 lg:px-8">
      <div className="rounded-2xl border border-[#293650] bg-[#111a2e]/60 p-5 sm:p-8">
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-violet-300">Model evaluation</p>
            <h2 id="evaluation-title" className="mt-2 text-2xl font-semibold tracking-[-0.03em]">How the models perform</h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-[#64748b]">{description}</p>
          </div>
          <div className="hidden rounded-xl border border-violet-400/20 bg-violet-400/10 p-3 text-violet-200 sm:block"><BarChart3 className="size-5" aria-hidden /></div>
        </div>

        {entries.length > 0 && (
          <div className="mt-6 flex w-full max-w-md gap-1 rounded-xl border border-[#293650] bg-[#111a2e] p-1">
            {(['selected', 'compare'] as const).map((option) => (
              <button
                key={option}
                type="button"
                aria-pressed={view === option}
                onClick={() => setView(option)}
                className={`flex-1 rounded-lg px-3 py-1.5 text-xs transition-colors duration-200 focus-visible:outline-2 focus-visible:outline-violet-400 ${view === option ? 'bg-violet-400/15 font-medium text-violet-100 ring-1 ring-violet-400/30' : 'text-[#94a3b8] hover:bg-white/[0.04] hover:text-[#e8edfa]'}`}
              >
                {option === 'selected' ? 'Selected Model' : 'Compare Models'}
              </button>
            ))}
          </div>
        )}

        {entries.length > 0 && (
          // min-h keeps the card from jumping when switching between the single-model and comparison layouts.
          <div className="mt-7 min-h-[15rem]">
            <div
              key={view === 'selected' ? `selected-${activeModelId}` : 'compare'}
              className="animate-in fade-in duration-300 motion-reduce:animate-none"
            >
              {view === 'selected' ? renderSelected() : renderCompare()}
            </div>
          </div>
        )}
        {entries.length === 0 && !loading && (
          <div className="mt-7 rounded-xl border border-white/[0.06] bg-[#0b1020] p-4 text-sm text-[#64748b]">
            No evaluation metrics are currently available from the backend.
          </div>
        )}
      </div>
    </section>
  )
}
