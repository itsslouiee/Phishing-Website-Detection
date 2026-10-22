export function Footer() {
  return (
    <footer className="border-t border-line/60 px-5 py-10 lg:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-ink">Phishing Website Detector</p>
          <p className="mt-2 max-w-md text-xs leading-5 text-ink-3">
            An educational machine learning project. Predictions are indicators, not guarantees, and can be wrong. Never
            rely on them alone to judge whether a website is safe.
          </p>
        </div>
        <p className="text-xs text-ink-3">© 2026 Phishing Website Detector</p>
      </div>
    </footer>
  )
}
