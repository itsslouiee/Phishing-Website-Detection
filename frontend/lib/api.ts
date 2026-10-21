export type AnalysisMode = 'best' | 'specific'

export type ModelOption = {
  id: string
  label: string
}

export type AnalysisResult = {
  verdict: 'legitimate' | 'phishing'
  confidence?: number
  modelName?: string
  status: string
  explanation?: string
  features?: Record<string, string | number | boolean>
  simulated: boolean
}

export type AnalyzeRequest = { url: string; mode: AnalysisMode; model?: string }

export type BackendModelInfo = {
  id: string
  name: string
}

export type BackendEvaluationEntry = {
  model: BackendModelInfo
  is_default: boolean
  accuracy: number
  precision: number
  recall: number
  f1: number
}

export type BackendModelsResponse = {
  models: BackendModelInfo[]
  default_model: string | null
  ready: boolean
  issues: string[]
}

export type BackendEvaluationResponse = {
  available: boolean
  method: string
  note: string
  models: BackendEvaluationEntry[]
}

type BackendPrediction = {
  model: { id: string; name: string }
  prediction: 'legitimate' | 'phishing'
  label: 0 | 1
  confidence: number
  probabilities: { legitimate: number; phishing: number }
}

type BackendPredictResponse = {
  url: string
  results: BackendPrediction[]
}

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true'

function toResult(payload: BackendPredictResponse): AnalysisResult {
  const primary = payload.results[0]
  if (!primary) {
    throw new Error('The backend returned no predictions.')
  }

  const modelLabel = primary.model.name

  return {
    verdict: primary.prediction,
    confidence: primary.confidence,
    modelName: modelLabel,
    status: 'Analysis complete',
    explanation: `${modelLabel} predicted ${primary.prediction} with ${(primary.confidence * 100).toFixed(1)}% confidence.`,
    simulated: false,
  }
}

export async function analyzeUrl(request: AnalyzeRequest): Promise<AnalysisResult> {
  if (DEMO_MODE || !API_BASE_URL) {
    await new Promise((resolve) => setTimeout(resolve, 850))
    return {
      verdict: 'legitimate',
      status: 'Demo response',
      modelName: 'Demo mode',
      explanation: 'This is a simulated interface response. Set NEXT_PUBLIC_DEMO_MODE=false and configure NEXT_PUBLIC_API_BASE_URL to use the FastAPI backend.',
      simulated: true,
    }
  }

  const body: Record<string, string | undefined> = { url: request.url }
  if (request.mode === 'specific' && request.model) {
    body.model = request.model
  }

  const response = await fetch(`${API_BASE_URL}/api/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    let message = `Analysis failed with status ${response.status}`
    try {
      const payload = await response.json()
      if (payload?.detail) message = payload.detail
      if (payload?.code) message = `${payload.code}: ${payload.detail}`
    } catch {
      // ignore JSON parse failures and fall back to status text
    }
    throw new Error(message)
  }

  const payload: BackendPredictResponse = await response.json()
  return toResult(payload)
}

export async function getAvailableModels(): Promise<ModelOption[]> {
  if (DEMO_MODE || !API_BASE_URL) return []

  const response = await fetch(`${API_BASE_URL}/api/models`)
  if (!response.ok) throw new Error('Unable to load models')

  const json: BackendModelsResponse = await response.json()
  return json.models.map((model) => ({ id: model.id, label: model.name }))
}

export type ModelCatalog = { models: ModelOption[]; defaultModelId: string | null }

// Same GET /api/models endpoint as getAvailableModels, but keeps the backend's default_model (the best model).
export async function getModelCatalog(): Promise<ModelCatalog> {
  if (DEMO_MODE || !API_BASE_URL) return { models: [], defaultModelId: null }

  const response = await fetch(`${API_BASE_URL}/api/models`, { cache: 'no-store' })
  if (!response.ok) throw new Error('Unable to load models')

  const json: BackendModelsResponse = await response.json()
  return {
    models: json.models.map((model) => ({ id: model.id, label: model.name })),
    defaultModelId: json.default_model ?? null,
  }
}

export async function getEvaluationMetrics(): Promise<BackendEvaluationResponse | null> {
  if (DEMO_MODE || !API_BASE_URL) return null

  const response = await fetch(`${API_BASE_URL}/api/evaluation`, { cache: 'no-store' })
  if (!response.ok) throw new Error('Unable to load evaluation metrics')

  return response.json() as Promise<BackendEvaluationResponse>
}
