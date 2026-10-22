import { ArrowDown, ArrowRight, BrainCircuit, Link2, ShieldCheck, SlidersHorizontal, type LucideIcon } from 'lucide-react'
import { SectionHeading } from './section-heading'

const STAGES: { title: string; text: string; icon: LucideIcon }[] = [
  { title: 'URL Input', text: 'You paste a link into the analyzer.', icon: Link2 },
  { title: 'Feature Extraction', text: 'The URL is turned into the numeric features the models were trained on.', icon: SlidersHorizontal },
  { title: 'Model Inference', text: 'XGBoost, Random Forest and Logistic Regression each score those features.', icon: BrainCircuit },
  { title: 'Prediction', text: 'You get a phishing or legitimate label, with a probability when available.', icon: ShieldCheck },
]

function Connector() {
  return (
    <div className="flex flex-col items-center justify-center py-1 text-lilac/70 lg:flex-row lg:px-1 lg:py-0" aria-hidden="true">
      <div className="relative h-8 w-px bg-line lg:h-px lg:w-8">
        <span className="absolute left-1/2 size-1.5 -translate-x-1/2 animate-flow-y rounded-full bg-lilac lg:left-0 lg:top-1/2 lg:-translate-y-1/2 lg:translate-x-0 lg:animate-flow-x" />
      </div>
      <ArrowDown className="-mt-1 size-4 lg:hidden" />
      <ArrowRight className="-ml-1 hidden size-4 lg:block" />
    </div>
  )
}

export function Workflow() {
  return (
    <section id="workflow" aria-labelledby="workflow-title" className="border-t border-line/60 px-5 py-20 sm:py-28 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="reveal">
          <SectionHeading
            eyebrow="The workflow"
            title="From URL to prediction."
            titleId="workflow-title"
            description="Four stages turn a link into a classification."
          />
        </div>

        <ol className="mt-12 flex flex-col items-stretch lg:flex-row lg:items-stretch">
          {STAGES.map((stage, index) => (
            <li key={stage.title} className="contents">
              <div className="reveal group flex-1 rounded-2xl border border-line bg-surface/70 p-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-violet/50">
                <div className="flex items-center justify-between">
                  <span className="grid size-11 place-items-center rounded-xl border border-violet/25 bg-violet/10 text-lilac transition-colors group-hover:bg-violet/20">
                    <stage.icon className="size-5" aria-hidden="true" />
                  </span>
                  <span className="font-mono text-xs text-ink-3">0{index + 1}</span>
                </div>
                <h3 className="mt-6 text-base font-semibold text-ink">{stage.title}</h3>
                <p className="mt-2 text-sm leading-6 text-ink-2">{stage.text}</p>
              </div>
              {index < STAGES.length - 1 && <Connector />}
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
