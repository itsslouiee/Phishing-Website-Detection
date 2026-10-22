/**
 * Environment-driven configuration.
 *
 * NEXT_PUBLIC_* variables are inlined at build time, so they must be referenced
 * as literal `process.env.NEXT_PUBLIC_…` expressions (no dynamic lookups).
 */

function cleanBaseUrl(value: string | undefined): string | null {
  const trimmed = value?.trim()
  return trimmed ? trimmed.replace(/\/+$/, '') : null
}

function httpUrlOrNull(value: string | undefined): string | null {
  const trimmed = value?.trim()
  if (!trimmed) return null
  try {
    const url = new URL(trimmed)
    return url.protocol === 'https:' || url.protocol === 'http:' ? url.toString() : null
  } catch {
    return null
  }
}

/** Base URL of the FastAPI backend (no trailing slash), or null when unset. */
export const API_BASE_URL = cleanBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL)

/** Repository URL for the header link, or null when unset or invalid. */
export const GITHUB_URL = httpUrlOrNull(process.env.NEXT_PUBLIC_GITHUB_URL)
