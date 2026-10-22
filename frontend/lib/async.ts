import { ApiError, type ApiErrorKind } from './api'

/** Shared shape for anything loaded from the API. */
export type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; message: string; kind?: ApiErrorKind }

export type ErrorState = Extract<AsyncState<never>, { status: 'error' }>

export function toErrorState(error: unknown): ErrorState {
  if (error instanceof ApiError) return { status: 'error', message: error.message, kind: error.kind }
  return { status: 'error', message: 'Something went wrong. Please try again.' }
}
