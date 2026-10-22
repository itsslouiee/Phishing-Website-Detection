/** The three models compared by the app. Order here is the display order everywhere. */
export const MODEL_IDS = ['xgboost', 'random_forest', 'logistic_regression'] as const

export type ModelId = (typeof MODEL_IDS)[number]

/** XGBoost produces the main prediction in the URL analysis section. */
export const PRIMARY_MODEL: ModelId = 'xgboost'

type ModelMeta = {
  name: string
  /** Short label that identifies a model without relying on color. */
  abbr: string
  /** Identity color used in charts and cards. */
  color: string
}

export const MODEL_META: Record<ModelId, ModelMeta> = {
  xgboost: { name: 'XGBoost', abbr: 'XGB', color: '#8b5cf6' },
  random_forest: { name: 'Random Forest', abbr: 'RF', color: '#5b8cff' },
  logistic_regression: { name: 'Logistic Regression', abbr: 'LR', color: '#f0a5e6' },
}
