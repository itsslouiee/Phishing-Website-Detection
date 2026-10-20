import { Cpu, Globe, ListChecks, ScanSearch } from 'lucide-react'

const STEPS = [
  { icon: Globe, title: 'Website Input', text: 'You submit the URL of the website you want to check.' },
  { icon: ListChecks, title: 'Feature Extraction', text: 'Relevant characteristics of the URL are extracted and prepared as the input features the model expects.' },
  { icon: Cpu, title: 'Model Inference', text: 'The selected trained machine learning model analyzes the prepared features. It does not read the page’s raw HTML.' },
  { icon: ScanSearch, title: 'Prediction', text: 'The classification result, phishing or legitimate, is shown to you as an indicator to inform your next step.' },
]

export function WorkflowSection() {
  return (
    <section id="how-it-works" aria-labelledby="workflow-title" className="relative mx-auto max-w-5xl scroll-mt-6 px-5 pb-24 lg:px-8">
      <div className="mb-8 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-violet-300">The workflow</p>
          <h2 id="workflow-title" className="mt-2 text-2xl font-semibold tracking-[-0.03em] sm:text-3xl">From URL to prediction.</h2>
        </div>
        <p className="max-w-xs text-sm leading-6 text-[#64748b]">A focused pipeline for turning URL features into a useful first layer of defense.</p>
      </div>
      <ol className="grid gap-px overflow-hidden rounded-2xl border border-[#293650] bg-[#293650] sm:grid-cols-2 lg:grid-cols-4">
        {STEPS.map(({ icon: Icon, title, text }, i) => (
          <li key={title} className="bg-[#111a2e] p-6 transition-colors hover:bg-[#141f36]">
            <div className="flex items-center justify-between">
              <span className="grid size-9 place-items-center rounded-lg border border-violet-400/25 bg-violet-400/10 text-violet-300"><Icon className="size-4" aria-hidden /></span>
              <span className="font-mono text-xs text-[#64748b]">0{i + 1}</span>
            </div>
            <h3 className="mt-8 text-base font-medium">{title}</h3>
            <p className="mt-2 text-sm leading-6 text-[#64748b]">{text}</p>
          </li>
        ))}
      </ol>
    </section>
  )
}
