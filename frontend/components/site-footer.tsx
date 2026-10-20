import { PROJECT_NAME } from '@/lib/config'

export function SiteFooter() {
  return (
    <footer className="relative border-t border-[#293650]/70 px-5 py-8 lg:px-8">
      <div className="mx-auto flex max-w-5xl flex-col items-center gap-2 text-center text-xs leading-5 text-[#64748b] sm:flex-row sm:justify-between sm:text-left">
        <p className="font-medium text-[#94a3b8]">© {new Date().getFullYear()} {PROJECT_NAME}</p>
        <p>An educational machine learning project. Predictions are indicators, not guarantees.</p>
      </div>
    </footer>
  )
}
