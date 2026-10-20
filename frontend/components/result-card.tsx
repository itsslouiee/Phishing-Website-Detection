import { ShieldCheck, TriangleAlert } from 'lucide-react'
import { StatusPill } from '@/components/status-pill'
import type { AnalysisResult } from '@/lib/api'

export function ResultCard({ result }: { result: AnalysisResult }) {
  const phishing = result.verdict === 'phishing'
  return (
    <section aria-live="polite" className={`mt-4 rounded-2xl border p-5 ${phishing ? 'border-red-400/25 bg-red-400/[0.06]' : 'border-emerald-400/25 bg-emerald-400/[0.06]'}`}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className={`grid size-10 shrink-0 place-items-center rounded-xl ${phishing ? 'bg-red-400/15 text-red-300' : 'bg-emerald-400/15 text-emerald-300'}`}>
            {phishing ? <TriangleAlert className="size-5" aria-hidden /> : <ShieldCheck className="size-5" aria-hidden />}
          </div>
          <div>
            <p className="text-xs text-[#94a3b8]">Analysis verdict</p>
            <h3 className="mt-1 text-lg font-semibold text-[#e8edfa]">{phishing ? 'Potential phishing' : 'Potentially legitimate'}</h3>
          </div>
        </div>
        <StatusPill tone={phishing ? 'red' : 'green'}>{result.simulated ? 'Simulated result' : 'Analysis complete'}</StatusPill>
      </div>
      <div className="mt-5 grid gap-3 border-t border-white/[0.07] pt-4 sm:grid-cols-3">
        {result.confidence != null && (
          <div><p className="text-[11px] uppercase tracking-[0.13em] text-[#64748b]">Confidence</p><p className="mt-1 font-mono text-sm text-[#e8edfa]">{Math.round(result.confidence * 100)}%</p></div>
        )}
        <div><p className="text-[11px] uppercase tracking-[0.13em] text-[#64748b]">Model</p><p className="mt-1 text-sm text-[#c5cee0]">{result.modelName ?? 'Backend model pending'}</p></div>
        <div><p className="text-[11px] uppercase tracking-[0.13em] text-[#64748b]">Status</p><p className="mt-1 text-sm text-[#c5cee0]">{result.status}</p></div>
      </div>
      {result.explanation && <p className="mt-4 rounded-xl border border-white/[0.06] bg-black/10 p-3 text-xs leading-5 text-[#94a3b8]">{result.explanation}</p>}
    </section>
  )
}
