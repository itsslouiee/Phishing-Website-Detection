export type AnalysisMode = 'best' | 'specific' | 'compare'

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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE !== 'false'

export async function analyzeUrl(request: AnalyzeRequest): Promise<AnalysisResult> {
  if (DEMO_MODE || !API_BASE_URL) {
    await new Promise((resolve) => setTimeout(resolve, 850))
    return { verdict: 'legitimate', status: 'Demo response', modelName: 'Demo mode', explanation: 'This is a simulated interface response. Connect the FastAPI backend to receive a real prediction.', simulated: true }
  }
  const response = await fetch(`${API_BASE_URL}/analyze`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(request) })
  if (!response.ok) throw new Error(`Analysis failed with status ${response.status}`)
  return { ...(await response.json()), simulated: false }
}

export async function getAvailableModels() {
  if (!API_BASE_URL) return []
  const response = await fetch(`${API_BASE_URL}/models`)
  if (!response.ok) throw new Error('Unable to load models')
  return response.json()
}

export async function getEvaluationMetrics() {
  if (!API_BASE_URL) return null
  const response = await fetch(`${API_BASE_URL}/evaluation`)
  if (!response.ok) throw new Error('Unable to load evaluation metrics')
  return response.json()
}
