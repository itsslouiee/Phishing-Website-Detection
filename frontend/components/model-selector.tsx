import type { AnalysisMode, ModelOption } from '@/lib/api'

type Props = {
  mode: AnalysisMode
  model: string
  onModeChange: (mode: AnalysisMode) => void
  onModelChange: (model: string) => void
  availableModels: ModelOption[]
  defaultModelId: string | null
  loading?: boolean
  error?: string
}

const segment = (active: boolean) =>
  `rounded-lg px-3 py-1.5 text-xs transition-colors duration-200 focus-visible:outline-2 focus-visible:outline-violet-400 ${
    active ? 'bg-violet-400/15 font-medium text-violet-100 ring-1 ring-violet-400/30' : 'text-[#94a3b8] hover:bg-white/[0.04] hover:text-[#e8edfa]'
  }`

export function ModelSelector({ mode, model, onModeChange, onModelChange, availableModels, defaultModelId, loading, error }: Props) {
  const bestLabel = availableModels.find((option) => option.id === defaultModelId)?.label ?? defaultModelId
  const disabled = loading || !availableModels.length

  // Text announced to screen readers and shown in the best-model pill; always derived from the backend value.
  const status = loading
    ? 'Loading models…'
    : error
      ? 'Model unavailable'
      : mode === 'best'
        ? bestLabel
          ? `Best Model · ${bestLabel}`
          : 'Best model not available'
        : `${availableModels.find((option) => option.id === model)?.label ?? 'Choose a model'}`

  return (
    <fieldset className="mt-5 min-w-0 border-t border-white/[0.06] pt-4">
      <legend className="sr-only">Model selection</legend>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-[#64748b]">Model</p>
        <div role="group" aria-label="Model selection method" className="grid w-full max-w-md grid-cols-2 gap-1 rounded-xl border border-[#293650] bg-[#111a2e] p-1">
          <button type="button" aria-pressed={mode === 'best'} onClick={() => onModeChange('best')} className={segment(mode === 'best')}>
            Best Model
          </button>
          <button type="button" aria-pressed={mode === 'specific'} onClick={() => onModeChange('specific')} className={segment(mode === 'specific')}>
            Choose a Model
          </button>
        </div>
      </div>

      {/* Fixed-height slot so switching between the two methods never shifts the layout. */}
      <div className="mt-3 h-10">
        {mode === 'specific' ? (
          <select
            aria-label="Model"
            value={model}
            onChange={(e) => onModelChange(e.target.value)}
            disabled={disabled}
            className="h-10 w-full rounded-lg border border-[#293650] bg-[#111a2e] px-3 text-xs text-[#e8edfa] outline-none transition-colors hover:border-[#3a4a6b] focus:border-violet-400/70 focus:ring-2 focus:ring-violet-400/15 disabled:opacity-60"
          >
            {availableModels.map((option) => (
              <option key={option.id} value={option.id}>{option.label}</option>
            ))}
          </select>
        ) : (
          <div className="flex h-10 items-center gap-2 rounded-lg border border-violet-400/20 bg-violet-400/[0.07] px-3 text-xs text-violet-100">
            <span className="size-1.5 shrink-0 rounded-full bg-violet-300" aria-hidden />
            <span className="truncate">{status}</span>
          </div>
        )}
      </div>
      <p className="sr-only" aria-live="polite">Selected: {status}</p>
    </fieldset>
  )
}
