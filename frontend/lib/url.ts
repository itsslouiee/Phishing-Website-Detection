const MAX_URL_LENGTH = 2048

export type UrlValidation = { ok: true; url: string } | { ok: false; message: string }

/** Client-side sanity check before sending a URL to the backend. */
export function validateUrl(input: string): UrlValidation {
  const value = input.trim()
  if (!value) return { ok: false, message: 'Paste a URL to analyze.' }
  if (value.length > MAX_URL_LENGTH) {
    return { ok: false, message: `That URL is too long (limit ${MAX_URL_LENGTH} characters).` }
  }
  if (/\s/.test(value)) return { ok: false, message: 'URLs cannot contain spaces.' }

  let parsed: URL
  try {
    parsed = new URL(value)
  } catch {
    return { ok: false, message: 'Enter a full URL, including http:// or https://' }
  }
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    return { ok: false, message: 'Only http:// and https:// URLs can be analyzed.' }
  }
  if (!parsed.hostname) return { ok: false, message: 'That URL is missing a host name.' }
  return { ok: true, url: value }
}
