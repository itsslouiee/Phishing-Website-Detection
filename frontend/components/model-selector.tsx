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

export function ModelSelector({
  mode,
  model,
  onModeChange,
  onModelChange,
  availableModels,
  defaultModelId,
  loading,
  error,
}: Props) {
  const currentLabel =
    mode === 'best'
      ? defaultModelId
        ? `Best Model (${availableModels.find((option) => option.id === defaultModelId)?.label ?? defaultModelId})`
        : 'Best Model'
      : availableModels.find((option) => option.id === model)?.label ?? 'Choose a model'

  const handleSelection = (value: string) => {
    if (value === 'best') {
      onModeChange('best')
      onModelChange('')
      return
    }

    onModeChange('specific')
    onModelChange(value)
  }

  return (
    <fieldset className="mt-5 min-w-0 border-t border-white/[0.06] pt-4">
      <legend className="sr-only">Model selection</legend>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-[#64748b]">Model</p>
        <div role="radiogroup" aria-label="Model selection" className="grid w-full max-w-md grid-cols-2 gap-1 rounded-xl border border-[#293650] bg-[#111a2e] p-1">
          <button
            type="button"
            role="radio"
            aria-checked={mode === 'best'}
            onClick={() => {
              onModeChange('best')
              onModelChange('')
            }}
            className={`rounded-lg px-3 py-1.5 text-xs transition-colors focus-visible:outline-2 focus-visible:outline-violet-400 ${mode === 'best' ? 'bg-violet-400/15 font-medium text-violet-100 ring-1 ring-violet-400/30' : 'text-[#94a3b8] hover:bg-white/[0.04] hover:text-[#e8edfa]'}`}
          >
            Best Model
          </button>
          <button
            type="button"
            role="radio"
            aria-checked={mode === 'specific'}
            onClick={() => onModeChange('specific')}
            className={`rounded-lg px-3 py-1.5 text-xs transition-colors focus-visible:outline-2 focus-visible:outline-violet-400 ${mode === 'specific' ? 'bg-violet-400/15 font-medium text-violet-100 ring-1 ring-violet-400/30' : 'text-[#94a3b8] hover:bg-white/[0.04] hover:text-[#e8edfa]'}`}
          >
            Choose a Model
          </button>
        </div>
      </div>

      {mode === 'specific' && (
        <select
          aria-label="Model"
          value={model}
          onChange={(e) => handleSelection(e.target.value)}
          className="mt-3 h-10 w-full rounded-lg border border-[#293650] bg-[#111a2e] px-3 text-xs text-[#e8edfa] outline-none focus:border-violet-400/70 focus:ring-2 focus:ring-violet-400/15"
          disabled={loading || !availableModels.length}
        >
          <option value="">Select a model…</option>
          {availableModels.map((option) => (
            <option key={option.id} value={option.id}>{option.label}</option>
          ))}
        </select>
      )}

      <p className="mt-3 text-[11px] leading-5 text-[#64748b]" aria-live="polite">
        <span className="text-[#94a3b8]">Selected:</span> {loading ? 'Loading models…' : error ? 'Model unavailable' : currentLabel}
      </p>
    </fieldset>
  )
}
