import type { CSSProperties } from 'react'
import { formatPercent } from '@/lib/format'

/**
 * Semicircle gauge for the phishing probability (0–100%).
 * The arc is drawn with pathLength=100 so the dash math is just percentage points.
 */
export function ProbabilityArc({ value, tone }: { value: number; tone: 'danger' | 'safe' }) {
  const color = tone === 'danger' ? 'var(--color-danger)' : 'var(--color-safe)'
  const offset = 100 - Math.round(value * 1000) / 10
  const arc = 'M 12 60 A 48 48 0 0 1 108 60'

  return (
    <figure className="w-full max-w-[260px]">
      <div className="relative">
        <svg viewBox="0 0 120 70" className="w-full" role="img" aria-label={`Phishing probability ${formatPercent(value)}`}>
          <path d={arc} pathLength={100} fill="none" stroke="var(--color-line)" strokeWidth="8" strokeLinecap="round" opacity="0.7" />
          <path
            d={arc}
            pathLength={100}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray="100"
            strokeDashoffset={offset}
            className="animate-arc"
            style={{ '--off': String(offset) } as CSSProperties}
          />
        </svg>
        <div className="absolute inset-x-0 bottom-[10%] text-center">
          <p className="font-mono text-4xl font-semibold leading-none tracking-tight tabular-nums text-ink">{formatPercent(value)}</p>
        </div>
        <span className="absolute -bottom-1 left-0 font-mono text-[10px] text-ink-3" aria-hidden="true">0%</span>
        <span className="absolute -bottom-1 right-0 font-mono text-[10px] text-ink-3" aria-hidden="true">100%</span>
      </div>
      <figcaption className="mt-4 text-center text-xs text-ink-2">Phishing probability</figcaption>
    </figure>
  )
}
