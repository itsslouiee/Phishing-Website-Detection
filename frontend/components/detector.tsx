'use client'

import { useAnalysis } from '@/hooks/use-analysis'
import { useApiResource } from '@/hooks/use-api-resource'
import { useHealth } from '@/hooks/use-health'
import { getEvaluation } from '@/lib/api'
import { ModelSection } from './model-section'
import { UrlAnalyzer } from './url-analyzer'

/**
 * Owns the shared state for sections 1 and 2: one analysis feeds both the main
 * XGBoost result and the three-model comparison; evaluation metrics load on their own.
 */
export function Detector() {
  const analysis = useAnalysis()
  const health = useHealth()
  const evaluation = useApiResource(getEvaluation)

  return (
    <>
      <UrlAnalyzer
        url={analysis.url}
        predict={analysis.predict}
        health={health}
        onAnalyze={analysis.analyze}
        onRetry={analysis.retryPredict}
      />
      <ModelSection
        url={analysis.url}
        compare={analysis.compare}
        evaluation={evaluation.state}
        onRetryCompare={analysis.retryCompare}
        onRetryEvaluation={evaluation.retry}
      />
    </>
  )
}
