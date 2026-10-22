import type { ReactNode } from 'react'
import type { AsyncState } from '@/lib/async'
import type { CompareResponse, EvaluationResponse } from '@/lib/schemas'
import { EvaluationPanel } from './evaluation-panel'
import { SectionHeading } from './section-heading'
import { UrlPredictions } from './url-predictions'

function Panel({
  chip,
  title,
  description,
  children,
}: {
  chip: string
  title: string
  description: string
  children: ReactNode
}) {
  return (
    <div className="rounded-3xl border border-line bg-surface/60 p-5 sm:p-8">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold tracking-tight text-ink">{title}</h3>
          <p className="mt-1 max-w-xl text-sm leading-6 text-ink-2">{description}</p>
        </div>
        <span className="w-fit shrink-0 rounded-full border border-line px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-2">
          {chip}
        </span>
      </div>
      {children}
    </div>
  )
}

export function ModelSection({
  url,
  compare,
  evaluation,
  onRetryCompare,
  onRetryEvaluation,
}: {
  url: string | null
  compare: AsyncState<CompareResponse>
  evaluation: AsyncState<EvaluationResponse>
  onRetryCompare: () => void
  onRetryEvaluation: () => void
}) {
  return (
    <section id="evaluation" aria-labelledby="evaluation-title" className="border-t border-line/60 px-5 py-20 sm:py-28 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="reveal">
          <SectionHeading
            eyebrow="Model evaluation"
            title="Three models, one URL."
            titleId="evaluation-title"
            description="See how XGBoost, Random Forest and Logistic Regression each classify the exact URL you analyzed."
          />
        </div>

        <div className="mt-10 space-y-6">
          <Panel
            chip="This URL"
            title="Predictions for this URL"
            description="What each model predicted for the exact URL analyzed above."
          >
            <UrlPredictions url={url} state={compare} onRetry={onRetryCompare} />
          </Panel>
        </div>
      </div>
    </section>
  )
}
