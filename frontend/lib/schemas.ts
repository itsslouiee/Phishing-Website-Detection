import { z } from 'zod'
import { MODEL_IDS } from './models'

/**
 * Runtime schemas for every API response. Anything that does not match is
 * rejected as an "invalid response" instead of being rendered.
 * Keep in sync with API_CONTRACT.md.
 */

const probability = z.number().min(0).max(1)
const count = z.number().int().nonnegative()

export const modelIdSchema = z.enum(MODEL_IDS)
export const labelSchema = z.enum(['phishing', 'legitimate'])

// GET /health
export const healthSchema = z.object({
  status: z.enum(['ok', 'degraded']),
  models: z.object({
    xgboost: z.boolean(),
    random_forest: z.boolean(),
    logistic_regression: z.boolean(),
  }),
})

// GET /api/v1/evaluation
export const confusionMatrixSchema = z.object({
  tn: count,
  fp: count,
  fn: count,
  tp: count,
})

export const modelEvaluationSchema = z.object({
  model: modelIdSchema,
  metrics: z.object({
    accuracy: probability,
    precision: probability,
    recall: probability,
    f1: probability,
    roc_auc: probability.nullish(),
  }),
  confusion_matrix: confusionMatrixSchema.nullish(),
})

export const evaluationResponseSchema = z.object({
  evaluation_samples: count.nullish(),
  models: z.array(modelEvaluationSchema).min(1),
})

// POST /api/v1/predict and /api/v1/compare
export const predictionSchema = z.object({
  model: modelIdSchema,
  label: labelSchema,
  phishing_probability: probability.nullish(),
})

export const predictResponseSchema = z.object({
  url: z.string(),
  model: z.literal('xgboost'),
  label: labelSchema,
  phishing_probability: probability.nullish(),
})

export const compareResponseSchema = z
  .object({
    url: z.string(),
    predictions: z.array(predictionSchema),
  })
  .refine((value) => MODEL_IDS.every((id) => value.predictions.some((p) => p.model === id)), {
    message: 'Response is missing a prediction for one of the three models.',
  })

// Error envelope returned with 4xx/5xx responses
export const apiErrorBodySchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
  }),
})

export type Health = z.infer<typeof healthSchema>
export type ModelEvaluation = z.infer<typeof modelEvaluationSchema>
export type ConfusionMatrixData = z.infer<typeof confusionMatrixSchema>
export type EvaluationResponse = z.infer<typeof evaluationResponseSchema>
export type Prediction = z.infer<typeof predictionSchema>
export type PredictResponse = z.infer<typeof predictResponseSchema>
export type CompareResponse = z.infer<typeof compareResponseSchema>
export type PredictionLabel = z.infer<typeof labelSchema>
