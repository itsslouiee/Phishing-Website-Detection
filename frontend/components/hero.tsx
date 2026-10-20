import { Analyzer } from '@/components/analyzer'
import { StatusPill } from '@/components/status-pill'

export function Hero() {
  return (
    <section id="top" aria-labelledby="hero-title" className="relative mx-auto max-w-6xl px-5 pb-12 pt-8 sm:pt-10 lg:px-8 lg:pb-16">
      <div className="mx-auto max-w-3xl text-center">
        <StatusPill>Machine learning · Web security</StatusPill>
        <h1 id="hero-title" className="mt-5 text-[2.5rem] leading-[1.02] font-semibold tracking-[-0.045em] text-balance uppercase sm:text-6xl lg:text-7xl">
          Check before<br />
          <span className="bg-gradient-to-r from-[#e8edfa] via-[#c9bcff] to-[#8b5cf6] bg-clip-text text-transparent">you click</span>
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-[#94a3b8] sm:text-base sm:leading-7">
          Analyze suspicious URLs with machine learning to help identify potential phishing websites.
        </p>
      </div>
      <div className="mt-7 sm:mt-8"><Analyzer /></div>
    </section>
  )
}
