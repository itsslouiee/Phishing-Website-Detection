import type { z } from 'zod'
import { API_BASE_URL } from './config'
import {
  apiErrorBodySchema,
  compareResponseSchema,
  evaluationResponseSchema,
  healthSchema,
  predictResponseSchema,
} from './schemas'

/**
 * API client. This is the only module that talks to the backend; UI components
 * never call fetch directly. Responses are validated at runtime, and failures
 * are surfaced as ApiError. Nothing is ever substituted or invented.
 */

const REQUEST_TIMEOUT_MS = 20_000

export type ApiErrorKind = 'config' | 'network' | 'timeout' | 'http' | 'invalid_response'

export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number
  readonly code?: string

  constructor(kind: ApiErrorKind, message: string, options: { status?: number; code?: string } = {}) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = options.status
    this.code = options.code
  }
}

type RequestOptions = {
  method?: 'GET' | 'POST'
  body?: unknown
  signal?: AbortSignal
}

async function readErrorBody(response: Response): Promise<{ code?: string; message?: string }> {
  try {
    const parsed = apiErrorBodySchema.safeParse(await response.json())
    return parsed.success ? parsed.data.error : {}
  } catch {
    return {}
  }
}

async function request<S extends z.ZodType>(
  path: string,
  schema: S,
  { method = 'GET', body, signal }: RequestOptions = {},
): Promise<z.output<S>> {
  if (!API_BASE_URL) {
    throw new ApiError('config', 'The API address is not configured. Set NEXT_PUBLIC_API_BASE_URL and restart the app.')
  }

  const timeout = AbortSignal.timeout(REQUEST_TIMEOUT_MS)
  const combined = signal ? AbortSignal.any([signal, timeout]) : timeout

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: body === undefined ? { Accept: 'application/json' } : { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: combined,
      cache: 'no-store',
    })
  } catch (error) {
    // The caller cancelled on purpose (new request, unmount): let it handle that.
    if (signal?.aborted) throw error
    if (timeout.aborted) {
      throw new ApiError('timeout', 'The request took too long. Check that the backend is running and try again.')
    }
    throw new ApiError('network', "Couldn't reach the backend. Check your connection and that the API is running.")
  }

  if (!response.ok) {
    const detail = await readErrorBody(response)
    const rejected = response.status === 400 || response.status === 422
    const message = rejected
      ? (detail.message ?? 'The API rejected this URL.')
      : response.status === 503
        ? 'The models are not ready yet. Try again in a moment.'
        : `The API responded with an error (${response.status}).`
    throw new ApiError('http', message, { status: response.status, code: detail.code })
  }

  let payload: unknown
  try {
    payload = await response.json()
  } catch {
    throw new ApiError('invalid_response', 'The API returned a response that is not valid JSON.', { status: response.status })
  }

  const parsed = schema.safeParse(payload)
  if (!parsed.success) {
    throw new ApiError('invalid_response', 'The API returned data in an unexpected format.', { status: response.status })
  }
  return parsed.data
}

export function getHealth(signal?: AbortSignal) {
  return request('/health', healthSchema, { signal })
}

export function getEvaluation(signal?: AbortSignal) {
  return request('/api/v1/evaluation', evaluationResponseSchema, { signal })
}

export function predictUrl(url: string, signal?: AbortSignal) {
  return request('/api/v1/predict', predictResponseSchema, { method: 'POST', body: { url }, signal })
}

export function compareUrl(url: string, signal?: AbortSignal) {
  return request('/api/v1/compare', compareResponseSchema, { method: 'POST', body: { url }, signal })
}
