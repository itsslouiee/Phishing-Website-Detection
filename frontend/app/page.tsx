'use client'

import { useState } from 'react'
import { z } from 'zod'
import {
  ArrowRight,
  Check,
  ChevronDown,
  CircleAlert,
  ExternalLink,
  GitBranch,
  LockKeyhole,
  Radar,
  ScanLine,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
  WandSparkles,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { analyzeUrl, type AnalysisResult, type AnalysisMode } from '@/lib/api'

const urlSchema = z.string().trim().url('Enter a valid URL').refine((value) => {
  try {
    const protocol = new URL(value).protocol
    return protocol === 'http:' || protocol === 'https:'
  } catch {
    return false
  }
}, 'Use an http:// or https:// URL')

const modes: { value: AnalysisMode; label: string; description: string }[] = [
  { value: 'best', label: 'Best available model', description: 'Automatically select the strongest available model' },
  { value: 'specific', label: 'Select a specific model', description: 'Choose from backend-provided models' },
  { value: 'compare', label: 'Compare all available models', description: 'Run the URL against every available model' },
]

function Logo() {
  return <div className="flex items-center gap-3"><div className="relative grid size-9 place-items-center rounded-xl border border-violet-400/35 bg-violet-400/10 text-violet-300"><Radar className="size-5" /><span className="absolute inset-1 rounded-lg border border-violet-300/20" /></div><span className="text-[15px] font-semibold tracking-[-0.02em] text-[#e8edfa]">[PROJECT NAME]</span></div>
}

function StatusPill({ children, tone = 'violet' }: { children: React.ReactNode; tone?: 'violet' | 'green' | 'red' }) {
  const styles = { violet: 'border-violet-400/20 bg-violet-400/10 text-violet-200', green: 'border-emerald-400/20 bg-emerald-400/10 text-emerald-300', red: 'border-red-400/20 bg-red-400/10 text-red-300' }
  return <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[11px] font-medium tracking-[0.12em] uppercase ${styles[tone]}`}><span className="size-1.5 rounded-full bg-current" />{children}</span>
}

function ResultCard({ result }: { result: AnalysisResult }) {
  const phishing = result.verdict === 'phishing'
  return <section aria-live="polite" className={`mt-5 rounded-2xl border p-5 ${phishing ? 'border-red-400/25 bg-red-400/[0.06]' : 'border-emerald-400/25 bg-emerald-400/[0.06]'}`}>
    <div className="flex flex-wrap items-start justify-between gap-4"><div className="flex items-start gap-3"><div className={`grid size-10 shrink-0 place-items-center rounded-xl ${phishing ? 'bg-red-400/15 text-red-300' : 'bg-emerald-400/15 text-emerald-300'}`}>{phishing ? <TriangleAlert className="size-5" /> : <ShieldCheck className="size-5" />}</div><div><p className="text-xs text-[#94a3b8]">Analysis verdict</p><h3 className="mt-1 text-lg font-semibold text-[#e8edfa]">{phishing ? 'Potential phishing' : 'Potentially legitimate'}</h3></div></div><StatusPill tone={phishing ? 'red' : 'green'}>{result.simulated ? 'Simulated result' : 'Analysis complete'}</StatusPill></div>
    <div className="mt-5 grid gap-3 border-t border-white/[0.07] pt-4 sm:grid-cols-3">{result.confidence != null && <div><p className="text-[11px] uppercase tracking-[0.13em] text-[#64748b]">Confidence</p><p className="mt-1 font-mono text-sm text-[#e8edfa]">{Math.round(result.confidence * 100)}%</p></div>}<div><p className="text-[11px] uppercase tracking-[0.13em] text-[#64748b]">Model</p><p className="mt-1 text-sm text-[#c5cee0]">{result.modelName ?? 'Backend model pending'}</p></div><div><p className="text-[11px] uppercase tracking-[0.13em] text-[#64748b]">Status</p><p className="mt-1 text-sm text-[#c5cee0]">{result.status}</p></div></div>
    {result.explanation && <p className="mt-4 rounded-xl border border-white/[0.06] bg-black/10 p-3 text-xs leading-5 text-[#94a3b8]">{result.explanation}</p>}
  </section>
}

export default function Page() {
  const [url, setUrl] = useState('')
  const [mode, setMode] = useState<AnalysisMode>('best')
  const [model, setModel] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [showModes, setShowModes] = useState(false)

  async function handleAnalyze(event: React.FormEvent) {
    event.preventDefault(); setError(''); setResult(null)
    const parsed = urlSchema.safeParse(url)
    if (!parsed.success) { setError(parsed.error.issues[0]?.message ?? 'Enter a valid URL'); return }
    setLoading(true)
    try { setResult(await analyzeUrl({ url: parsed.data, mode, model: model || undefined })) } catch { setError('The analysis service is unavailable. Try again or check your backend URL.') } finally { setLoading(false) }
  }

  return <main className="min-h-screen overflow-hidden bg-[#0b1020] text-[#e8edfa] selection:bg-violet-400/30">
    <div className="pointer-events-none absolute inset-x-0 top-0 h-[580px] bg-[radial-gradient(ellipse_at_50%_-10%,rgba(139,92,246,0.16),transparent_62%)]" />
    <nav className="relative mx-auto flex max-w-6xl items-center justify-between px-5 py-5 lg:px-8"><Logo /><div className="hidden items-center gap-8 text-xs text-[#94a3b8] md:flex"><a className="transition-colors hover:text-[#e8edfa]" href="#how-it-works">How it works</a><a className="transition-colors hover:text-[#e8edfa]" href="#evaluation">Evaluation</a></div><a href="https://github.com" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-lg border border-[#293650] px-3 py-2 text-xs text-[#c5cee0] transition-colors hover:border-violet-400/50 hover:text-white"><GitBranch className="size-3.5" /> GitHub <ExternalLink className="size-3" /></a></nav>
    <div className="relative mx-auto max-w-6xl px-5 pb-20 pt-16 lg:px-8 lg:pt-24"><div className="mx-auto max-w-3xl text-center"><StatusPill>MACHINE LEARNING · WEB SECURITY</StatusPill><h1 className="mt-7 text-5xl font-semibold tracking-[-0.055em] text-balance sm:text-7xl">Know before<br /><span className="bg-gradient-to-r from-[#e8edfa] via-[#c9bcff] to-[#8b5cf6] bg-clip-text text-transparent">you click.</span></h1><p className="mx-auto mt-6 max-w-xl text-base leading-7 text-[#94a3b8]">Analyze suspicious URLs with machine learning to help identify potential phishing websites.</p></div>
      <div className="mx-auto mt-12 max-w-2xl"><div className="rounded-3xl border border-[#293650] bg-[#111a2e]/90 p-2 shadow-[0_24px_90px_rgba(0,0,0,0.3)] backdrop-blur"><form onSubmit={handleAnalyze} className="rounded-[20px] border border-white/[0.06] bg-[#0b1020] p-5 sm:p-6"><div className="mb-5 flex items-center justify-between"><div><p className="text-sm font-medium text-[#e8edfa]">Analyze a URL</p><p className="mt-1 text-xs text-[#64748b]">Check a website before you visit it</p></div><div className="grid size-9 place-items-center rounded-xl bg-violet-400/10 text-violet-300"><ScanLine className="size-4" /></div></div><label htmlFor="url" className="sr-only">URL to analyze</label><div className="flex flex-col gap-2 sm:flex-row"><input id="url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://example.com" className="h-12 min-w-0 flex-1 rounded-xl border border-[#293650] bg-[#111a2e] px-4 text-sm text-[#e8edfa] outline-none transition-colors placeholder:text-[#64748b] focus:border-violet-400/70 focus:ring-2 focus:ring-violet-400/15" aria-invalid={!!error} /> <Button type="submit" disabled={loading} className="h-12 rounded-xl bg-[#8b5cf6] px-5 font-medium text-white hover:bg-[#7c4fe4]">{loading ? 'Analyzing…' : 'Analyze URL'} {!loading && <ArrowRight data-icon="inline-end" />}</Button></div>{error && <p className="mt-3 flex items-center gap-2 text-xs text-red-300"><CircleAlert className="size-3.5" />{error}</p>}<div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><button type="button" onClick={() => setShowModes(!showModes)} className="flex items-center gap-2 text-xs text-[#94a3b8] transition-colors hover:text-[#e8edfa]"><WandSparkles className="size-3.5 text-violet-300" />{modes.find((item) => item.value === mode)?.label}<ChevronDown className={`size-3.5 transition-transform ${showModes ? 'rotate-180' : ''}`} /></button><span className="flex items-center gap-1.5 text-[11px] text-[#64748b]"><LockKeyhole className="size-3" /> URLs are processed for analysis</span></div>{showModes && <div className="mt-3 grid gap-2 rounded-xl border border-[#293650] bg-[#111a2e] p-2">{modes.map((item) => <button type="button" key={item.value} onClick={() => { setMode(item.value); setShowModes(false) }} className={`rounded-lg p-3 text-left transition-colors ${mode === item.value ? 'bg-violet-400/10' : 'hover:bg-white/[0.04]'}`}><div className="flex items-center justify-between"><span className="text-xs font-medium text-[#e8edfa]">{item.label}</span>{mode === item.value && <Check className="size-3.5 text-violet-300" />}</div><p className="mt-1 text-[11px] text-[#64748b]">{item.description}</p></button>)}</div>}{mode === 'specific' && <input value={model} onChange={(e) => setModel(e.target.value)} placeholder="Model identifier from backend configuration" className="mt-3 h-10 w-full rounded-lg border border-[#293650] bg-[#111a2e] px-3 text-xs text-[#e8edfa] outline-none focus:border-violet-400/70" />}</form></div>{result && <ResultCard result={result} />}<p className="mt-4 text-center text-[11px] leading-5 text-[#64748b]">An ML prediction is an indicator, not a guarantee of website safety.</p></div>
      <section id="how-it-works" className="mx-auto mt-32 max-w-5xl scroll-mt-20"><div className="mb-10 flex flex-col justify-between gap-3 sm:flex-row sm:items-end"><div><p className="text-xs font-medium uppercase tracking-[0.18em] text-violet-300">The workflow</p><h2 className="mt-3 text-2xl font-semibold tracking-[-0.03em] sm:text-3xl">From URL to signal.</h2></div><p className="max-w-xs text-sm leading-6 text-[#64748b]">A focused pipeline for turning URL structure into a useful first layer of defense.</p></div><div className="grid gap-px overflow-hidden rounded-2xl border border-[#293650] bg-[#293650] md:grid-cols-3">{[['01', 'Submit a URL', 'Paste a suspicious link into the analyzer for a quick, focused check.'], ['02', 'Extract features', 'Relevant URL characteristics are prepared for the trained model.'], ['03', 'Evaluate the signal', 'The model returns a prediction to help inform your next step.']].map(([number, title, text]) => <div key={number} className="bg-[#111a2e] p-6"><span className="font-mono text-xs text-violet-300">{number}</span><h3 className="mt-12 text-base font-medium">{title}</h3><p className="mt-3 text-sm leading-6 text-[#64748b]">{text}</p></div>)}</div></section>
      <section id="evaluation" className="mx-auto mt-24 max-w-5xl scroll-mt-20 rounded-2xl border border-[#293650] bg-[#111a2e]/60 p-6 sm:p-8"><div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-start"><div><p className="text-xs font-medium uppercase tracking-[0.18em] text-violet-300">Model evaluation</p><h2 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">Metrics when they&apos;re verified.</h2><p className="mt-3 max-w-lg text-sm leading-6 text-[#64748b]">Evaluation metrics will appear here once connected to the FastAPI backend. No placeholder numbers, no inflated claims.</p></div><div className="rounded-xl border border-violet-400/20 bg-violet-400/10 p-4 text-violet-200"><Sparkles className="size-5" /></div></div><div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">{['Accuracy', 'Precision', 'Recall', 'F1-score'].map((metric) => <div key={metric} className="rounded-xl border border-white/[0.06] bg-[#0b1020] p-4"><p className="text-xs text-[#64748b]">{metric}</p><p className="mt-3 font-mono text-lg text-[#64748b]">—</p><p className="mt-1 text-[10px] uppercase tracking-wider text-[#475569]">Awaiting data</p></div>)}</div></section>
    </div><footer className="relative border-t border-[#293650] px-5 py-7 lg:px-8"><div className="mx-auto flex max-w-6xl flex-col gap-4 text-xs text-[#64748b] sm:flex-row sm:items-center sm:justify-between"><span>Built as a machine-learning security project.</span><span className="flex items-center gap-2">[PROJECT NAME] <span className="text-[#293650]">·</span> <a href="https://github.com" className="transition-colors hover:text-[#e8edfa]">Repository ↗</a></span></div></footer>
  </main>
}
