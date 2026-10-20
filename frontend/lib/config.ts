import type { AnalysisMode } from '@/lib/api'

export const PROJECT_NAME = 'Phishing Website Detection'

/**
 * Default model selection.
 *
 * 'best' asks the backend to use its best-performing model, so the frontend
 * never has to hard-code which model that is.
 */
export const DEFAULT_ANALYSIS_MODE: AnalysisMode = 'best'

/**
 * TO CONFIRM: identifier (and display name) of the best-performing model,
 * taken from your own evaluation results. Leave null until verified; the UI
 * then shows "Best available model" without naming one.
 */
export const BEST_MODEL: { id: string; label: string } | null = null

/**
 * TO CONFIRM: models users may pick in "Select a specific model" mode.
 * While empty, a free-text model identifier field is shown instead
 * (existing behaviour). Later this can be filled from `GET /models`.
 */
export const MODEL_OPTIONS: { id: string; label: string }[] = []

export type EvaluationMetrics = {
  accuracy?: number
  precision?: number
  recall?: number
  f1?: number
}

export type ModelEvaluation = {
  modelId: string
  modelLabel: string
  /** Optional context, e.g. dataset name and test-split size. Only real values. */
  dataset?: string
  metrics: EvaluationMetrics
}

/**
 * TO CONFIRM: verified evaluation results, as fractions between 0 and 1
 * (0.973 renders as 97.3%). Leave empty until you have real numbers; the
 * section then shows an "awaiting data" state with no values.
 */
export const EVALUATION_RESULTS: ModelEvaluation[] = []
