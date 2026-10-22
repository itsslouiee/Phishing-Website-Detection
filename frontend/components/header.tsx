import { Radar } from 'lucide-react'
import { GITHUB_URL } from '@/lib/config'
import { GithubIcon } from './github-icon'

const NAV_LINKS = [
  { href: '#evaluation', label: 'Model evaluation' },
  { href: '#workflow', label: 'Workflow' },
]

export function Header() {
  return (
    <header className="relative z-10 border-b border-line/60">
      <div className="mx-auto grid h-16 max-w-6xl grid-cols-[1fr_auto_1fr] items-center gap-3 px-5 lg:px-8">
        <div className="flex items-center gap-3">
          <span className="relative grid size-9 shrink-0 place-items-center rounded-xl border border-violet/35 bg-violet/10 text-lilac">
            <Radar className="size-5" aria-hidden="true" />
            <span className="absolute inset-1 rounded-lg border border-lilac/15" aria-hidden="true" />
          </span>
          <span className="hidden text-[15px] font-semibold tracking-[-0.02em] text-ink sm:block">Phishing Website Detector</span>
          <span className="sr-only sm:hidden">Phishing Website Detector</span>
        </div>

        <nav aria-label="Page sections" className="flex items-center gap-1 sm:gap-2">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="rounded-lg px-2.5 py-2 text-xs font-medium text-ink-2 transition-colors hover:bg-white/[0.05] hover:text-ink sm:px-3 sm:text-sm"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex justify-end">
          {GITHUB_URL && (
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noreferrer noopener"
              aria-label="View the project on GitHub (opens in a new tab)"
              className="grid size-10 place-items-center rounded-xl border border-line text-ink-2 transition-colors hover:border-violet/60 hover:text-ink"
            >
              <GithubIcon className="size-5" />
            </a>
          )}
        </div>
      </div>
    </header>
  )
}
