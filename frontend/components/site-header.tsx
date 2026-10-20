import { ExternalLink, GitBranch, Radar } from 'lucide-react'
import { PROJECT_NAME } from '@/lib/config'

export function SiteHeader() {
  return (
    <header className="relative mx-auto flex max-w-6xl items-center justify-between px-5 py-4 lg:px-8">
      <a href="#top" className="flex items-center gap-3 rounded-lg focus-visible:outline-2 focus-visible:outline-violet-400">
        <span className="relative grid size-9 place-items-center rounded-xl border border-violet-400/35 bg-violet-400/10 text-violet-300">
          <Radar className="size-5" aria-hidden />
          <span className="absolute inset-1 rounded-lg border border-violet-300/20" />
        </span>
        <span className="text-[15px] font-semibold tracking-[-0.02em] text-[#e8edfa]">{PROJECT_NAME}</span>
      </a>
      <nav aria-label="Primary" className="hidden items-center gap-8 text-xs text-[#94a3b8] md:flex">
        <a className="transition-colors hover:text-[#e8edfa]" href="#evaluation">Evaluation</a>
        <a className="transition-colors hover:text-[#e8edfa]" href="#how-it-works">How it works</a>
      </nav>
      <a
        href="https://github.com"
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center gap-2 rounded-lg border border-[#293650] px-3 py-2 text-xs text-[#c5cee0] transition-colors hover:border-violet-400/50 hover:text-white"
      >
        <GitBranch className="size-3.5" aria-hidden /> GitHub <ExternalLink className="size-3" aria-hidden />
      </a>
    </header>
  )
}
