'use client'

import { useEffect, useState } from 'react'
import { z } from 'zod'
import { ArrowRight, CircleAlert, LockKeyhole } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ModelSelector } from '@/components/model-selector'
import { ResultCard } from '@/components/result-card'
import { analyzeUrl, getAvailableModels, type AnalysisMode, type AnalysisResult, type ModelOption } from '@/lib/api'
import { DEFAULT_ANALYSIS_MODE } from '@/lib/config'

const urlSchema = z.string().trim().url('Enter a valid URL').refine((value) => {
  try {
    const protocol = new URL(value).protocol
    return protocol === 'http:' || protocol === 'https:'
  } catch {
    return false
  }
}, 'Use an http:// or https:// URL')

export function Analyzer() {
  const [url, setUrl] = useState('')
  const [mode, setMode] = useState<AnalysisMode>(DEFAULT_ANALYSIS_MODE)
  const [model, setModel] = useState('')
  const [availableModels, setAvailableModels] = useState<ModelOption[]>([])
  const [defaultModelId, setDefaultModelId] = useState<string | null>(null)
  const [modelLoading, setModelLoading] = useState(true)
  const [modelError, setModelError] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let active = true

    async function loadModels() {
      try {
        const models = await getAvailableModels()
        if (!active) return

        setAvailableModels(models)
        setDefaultModelId(models.find((option) => option.id === 'xgboost')?.id ?? null)

        const response = await fetch(`${(process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')}/api/models`, { cache: 'no-store' })
        if (!response.ok) throw new Error('Unable to load backend model metadata')
        const payload = await response.json()

        if (payload?.default_model) {
          setDefaultModelId(payload.default_model)
        }
      } catch {
        if (active) {
          setModelError('Unable to load backend model metadata.')
        }
      } finally {
        if (active) {
          setModelLoading(false)
        }
      }
    }

    loadModels()
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return

    const activeModelId = mode === 'best' ? defaultModelId ?? '' : model
    window.dispatchEvent(new CustomEvent('phishing-model-selection', { detail: { modelId: activeModelId } }))
  }, [mode, model, defaultModelId])

  async function handleAnalyze(event: React.FormEvent) {
    event.preventDefault()
    setError('')
    setResult(null)
    const parsed = urlSchema.safeParse(url)
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? 'Enter a valid URL')
      return
    }
    setLoading(true)
    try {
      setResult(await analyzeUrl({ url: parsed.data, mode, model: mode === 'specific' ? model : undefined }))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'The analysis service is unavailable. Try again or check your backend URL.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto w-full max-w-2xl">
      <div className="rounded-3xl border border-[#293650] bg-[#111a2e]/90 p-2 shadow-[0_24px_90px_rgba(0,0,0,0.3)] backdrop-blur">
        <form onSubmit={handleAnalyze} noValidate className="rounded-[20px] border border-white/[0.06] bg-[#0b1020] p-4 sm:p-5">
          <label htmlFor="url" className="mb-2 block text-sm font-medium text-[#e8edfa]">Website URL</label>
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              id="url"
              type="url"
              inputMode="url"
              autoComplete="off"
              autoFocus
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              aria-invalid={!!error}
              aria-describedby={error ? 'url-error' : undefined}
              className="h-12 min-w-0 flex-1 rounded-xl border border-[#293650] bg-[#111a2e] px-4 text-sm text-[#e8edfa] outline-none transition-colors placeholder:text-[#64748b] hover:border-[#3a4a6b] focus:border-violet-400/70 focus:ring-2 focus:ring-violet-400/20 aria-[invalid=true]:border-red-400/60"
            />
            <Button type="submit" disabled={loading} className="h-12 rounded-xl bg-[#8b5cf6] px-6 font-medium text-white transition-colors hover:bg-[#7c4fe4] focus-visible:ring-2 focus-visible:ring-violet-300/50 disabled:opacity-70">
              {loading ? 'Analyzing…' : 'Analyze Website'} {!loading && <ArrowRight data-icon="inline-end" />}
            </Button>
          </div>
          {error && <p id="url-error" role="alert" className="mt-3 flex items-center gap-2 text-xs text-red-300"><CircleAlert className="size-3.5" aria-hidden />{error}</p>}

          <ModelSelector
            mode={mode}
            model={model}
            onModeChange={setMode}
            onModelChange={setModel}
            availableModels={availableModels}
            defaultModelId={defaultModelId}
            loading={modelLoading}
            error={modelError}
          />
        </form>
      </div>
      {result && <ResultCard result={result} />}
      <p className="mt-3 flex items-center justify-center gap-1.5 text-center text-[11px] leading-5 text-[#64748b]">
        <LockKeyhole className="size-3 shrink-0" aria-hidden /> An ML prediction is an indicator, not a guarantee of website safety.
      </p>
    </div>
  )
}
