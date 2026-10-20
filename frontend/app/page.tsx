import { EvaluationSection } from '@/components/evaluation-section'
import { Hero } from '@/components/hero'
import { SiteFooter } from '@/components/site-footer'
import { SiteHeader } from '@/components/site-header'
import { WorkflowSection } from '@/components/workflow-section'

export default function Page() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0b1020] text-[#e8edfa] selection:bg-violet-400/30">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[580px] bg-[radial-gradient(ellipse_at_50%_-10%,rgba(139,92,246,0.16),transparent_62%)]" aria-hidden />
      <SiteHeader />
      <main>
        <Hero />
        <EvaluationSection />
        <WorkflowSection />
      </main>
      <SiteFooter />
    </div>
  )
}
