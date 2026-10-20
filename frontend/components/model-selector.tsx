import { BEST_MODEL, MODEL_OPTIONS } from '@/lib/config'
import type { AnalysisMode } from '@/lib/api'

export const MODES: { value: AnalysisMode; label: string; short: string; description: string }[] = [
  { value: 'best', label: 'Best available model', short: 'Best model', description: 'Automatically uses the strongest available model' },
  { value: 'specific', label: 'Select a specific model', short: 'Choose model', description: 'Pick one model to run the URL against' },
  { value: 'compare', label: 'Compare all available models', short: 'Compare all', description: 'Run the URL against every available model' },
]

type Props = {
  mode: AnalysisMode
  model: string
  onModeChange: (mode: AnalysisMode) => void
  onModelChange: (model: string) => void
}

export function ModelSelector({ mode, model, onModeChange, onModelChange }: Props) {
  const active = MODES.find((m) => m.value === mode)!
  const selectedLabel =
    mode === 'best' && BEST_MODEL ? `${active.label} · ${BEST_MODEL.label}` : active.label

  return (
    <fieldset className="mt-5 min-w-0 border-t border-white/[0.06] pt-4">
      <legend className="sr-only">Model selection</legend>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-[#64748b]">Model</p>
        <div role="radiogroup" aria-label="Model selection" className="grid grid-cols-3 gap-1 rounded-xl border border-[#293650] bg-[#111a2e] p-1">
          {MODES.map((item) => {
            const checked = item.value === mode
            return (
              <button
                key={item.value}
                type="button"
                role="radio"
                aria-checked={checked}
                title={item.description}
                onClick={() => onModeChange(item.value)}
                className={`rounded-lg px-3 py-1.5 text-xs transition-colors focus-visible:outline-2 focus-visible:outline-violet-400 ${checked ? 'bg-violet-400/15 font-medium text-violet-100 ring-1 ring-violet-400/30' : 'text-[#94a3b8] hover:bg-white/[0.04] hover:text-[#e8edfa]'}`}
              >
                {item.short}
              </button>
            )
          })}
        </div>
      </div>

      {mode === 'specific' && (
        MODEL_OPTIONS.length > 0 ? (
          <select
            aria-label="Model"
            value={model}
            onChange={(e) => onModelChange(e.target.value)}
            className="mt-3 h-10 w-full rounded-lg border border-[#293650] bg-[#111a2e] px-3 text-xs text-[#e8edfa] outline-none focus:border-violet-400/70 focus:ring-2 focus:ring-violet-400/15"
          >
            <option value="">Select a model…</option>
            {MODEL_OPTIONS.map((o) => <option key={o.id} value={o.id}>{o.label}</option>)}
          </select>
        ) : (
          <input
            aria-label="Model identifier"
            value={model}
            onChange={(e) => onModelChange(e.target.value)}
            placeholder="Model identifier from backend configuration"
            className="mt-3 h-10 w-full rounded-lg border border-[#293650] bg-[#111a2e] px-3 text-xs text-[#e8edfa] outline-none placeholder:text-[#64748b] focus:border-violet-400/70 focus:ring-2 focus:ring-violet-400/15"
          />
        )
      )}

      <p className="mt-3 text-[11px] leading-5 text-[#64748b]" aria-live="polite">
        <span className="text-[#94a3b8]">Selected:</span> {selectedLabel}
        {mode === 'best' && !BEST_MODEL && ' — resolved by the backend'}
      </p>
    </fieldset>
  )
}
