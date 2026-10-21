import type { AnalysisMode, ModelOption } from '@/lib/api'

export const PROJECT_NAME = 'Phishing Website Detection'

export const DEFAULT_ANALYSIS_MODE: AnalysisMode = 'best'

export const BEST_MODEL: { id: string; label: string } | null = null

export const MODEL_OPTIONS: ModelOption[] = [
  { id: 'logistic_regression', label: 'Logistic Regression' },
  { id: 'random_forest', label: 'Random Forest' },
  { id: 'xgboost', label: 'XGBoost' },
]

export type EvaluationMetrics = {
  accuracy?: number
  precision?: number
  recall?: number
  f1?: number
}

export type ModelEvaluation = {
  modelId: string
  modelLabel: string
  dataset?: string
  metrics: EvaluationMetrics
}

export const EVALUATION_RESULTS: ModelEvaluation[] = []
