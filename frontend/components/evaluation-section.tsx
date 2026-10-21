'use client'

import { useEffect, useMemo, useState } from 'react'
import { BarChart3 } from 'lucide-react'
import { getAvailableModels, getEvaluationMetrics, type BackendEvaluationEntry, type BackendEvaluationResponse, type ModelOption } from '@/lib/api'
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
      <p className="mt-3 text-[11px] leading-4 text-[#64748b]">{has ? hint : 'Awaiting data'}</p>
    </div>
  )
}

export function EvaluationSection() {
  const [evaluation, setEvaluation] = useState<BackendEvaluationResponse | null>(null)
  const [models, setModels] = useState<ModelOption[]>([])
  const [defaultModelId, setDefaultModelId] = useState<string | null>(null)
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null)
  const [view, setView] = useState<'selected' | 'compare'>('selected')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const [availableModels, evaluationData] = await Promise.all([getAvailableModels(), getEvaluationMetrics()])
        if (!active) return

        setModels(availableModels)
        const backendDefault = await fetch(`${(process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')}/api/models`, { cache: 'no-store' })
        if (backendDefault.ok) {
          const payload = await backendDefault.json()
          if (payload?.default_model) {
            setDefaultModelId(payload.default_model)
            setSelectedModelId((current) => current ?? payload.default_model)
          }
        }
        setEvaluation(evaluationData)
        const defaultEntry = evaluationData?.models.find((entry) => entry.is_default)
        if (defaultEntry?.model.id) {
          setSelectedModelId((current) => current ?? defaultEntry.model.id)
        } else if (availableModels[0]?.id) {
          setSelectedModelId((current) => current ?? availableModels[0].id)
        }
      } catch {
        if (active) {
          setError('Unable to load evaluation metrics from the backend.')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    load()

    const handleSelection = (event: Event) => {
      const detail = (event as CustomEvent<{ modelId?: string }>).detail
      if (detail?.modelId) {
        setSelectedModelId(detail.modelId)
      }
    }

    window.addEventListener('phishing-model-selection', handleSelection)

    return () => {
      active = false
      window.removeEventListener('phishing-model-selection', handleSelection)
    }
  }, [])

  useEffect(() => {
    if (!selectedModelId && defaultModelId) {
      setSelectedModelId(defaultModelId)
    }
  }, [selectedModelId, defaultModelId])

  const entries = useMemo(() => evaluation?.models ?? [], [evaluation])
  const selectedEntry = useMemo(
    () => entries.find((entry) => entry.model.id === selectedModelId) ?? entries[0] ?? null,
    [entries, selectedModelId],
  )

  const visibleEntries = view === 'selected' ? (selectedEntry ? [selectedEntry] : []) : entries

  return (
    <section id="evaluation" aria-labelledby="evaluation-title" className="relative mx-auto max-w-5xl scroll-mt-6 px-5 pb-16 lg:px-8">
      <div className="rounded-2xl border border-[#293650] bg-[#111a2e]/60 p-5 sm:p-8">
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-violet-300">Model evaluation</p>
            <h2 id="evaluation-title" className="mt-2 text-2xl font-semibold tracking-[-0.03em]">How the models perform</h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-[#64748b]">
              {entries.length
                ? 'Metrics measured on held-out test data. They describe this evaluation only, not real-world effectiveness.'
                : loading
                  ? 'Loading evaluation metrics from the backend…'
                  : error
                    ? error
                    : 'Verified evaluation metrics will appear here once available. No placeholder numbers, no inflated claims.'}
            </p>
          </div>
          <div className="hidden rounded-xl border border-violet-400/20 bg-violet-400/10 p-3 text-violet-200 sm:block"><BarChart3 className="size-5" aria-hidden /></div>
        </div>

        {entries.length > 0 && (
          <div className="mt-6 flex w-full max-w-md gap-1 rounded-xl border border-[#293650] bg-[#111a2e] p-1">
            {(['selected', 'compare'] as const).map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setView(option)}
                className={`flex-1 rounded-lg px-3 py-1.5 text-xs transition-colors ${view === option ? 'bg-violet-400/15 font-medium text-violet-100 ring-1 ring-violet-400/30' : 'text-[#94a3b8] hover:bg-white/[0.04] hover:text-[#e8edfa]'}`}
              >
                {option === 'selected' ? 'Selected Model' : 'Compare Models'}
              </button>
            ))}
          </div>
        )}

        <div className="mt-7 space-y-6">
          {visibleEntries.length === 0 ? (
            <div className="rounded-xl border border-white/[0.06] bg-[#0b1020] p-4 text-sm text-[#64748b]">
              No evaluation metrics are currently available from the backend.
            </div>
          ) : (
            visibleEntries.map((entry) => (
              <div key={entry.model.id}>
                <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1">
                  <h3 className="text-sm font-medium text-[#e8edfa]">{entry.model.name}</h3>
                  {entry.is_default && (
                    <span className="rounded-full border border-violet-400/25 bg-violet-400/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-violet-200">Default · best model</span>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                  {METRICS.map((metric) => (
                    <MetricCard
                      key={metric.key}
                      label={metric.label}
                      hint={metric.hint}
                      value={entry[metric.key]}
                    />
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  )
}
