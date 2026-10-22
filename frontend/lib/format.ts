/** Formats a 0–1 fraction as a percentage string, e.g. 0.9734 → "97.3%". */
export function formatPercent(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)}%`
}

export function formatCount(value: number): string {
  return new Intl.NumberFormat('en-US').format(value)
}
