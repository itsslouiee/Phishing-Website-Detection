'use client'

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { getModelCatalog, type AnalysisMode, type ModelOption } from '@/lib/api'
import { DEFAULT_ANALYSIS_MODE } from '@/lib/config'

type ModelSelection = {
  mode: AnalysisMode
  model: string
  setMode: (mode: AnalysisMode) => void
  setModel: (model: string) => void
  availableModels: ModelOption[]
  /** The backend's best model (GET /api/models -> default_model). Null until loaded or if the backend has none. */
  defaultModelId: string | null
  /** The model id that live prediction AND the evaluation view are currently using. */
  activeModelId: string | null
  loading: boolean
  error: string
}

const ModelSelectionContext = createContext<ModelSelection | null>(null)

// Single source of truth for the selected model, shared by the analyzer and the evaluation section.
export function ModelSelectionProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<AnalysisMode>(DEFAULT_ANALYSIS_MODE)
  const [model, setModel] = useState('')
  const [availableModels, setAvailableModels] = useState<ModelOption[]>([])
  const [defaultModelId, setDefaultModelId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const catalog = await getModelCatalog()
        if (!active) return
        setAvailableModels(catalog.models)
        setDefaultModelId(catalog.defaultModelId)
      } catch {
        if (active) setError('Unable to load backend model metadata.')
      } finally {
        if (active) setLoading(false)
      }
    }

    load()
    return () => {
      active = false
    }
  }, [])

  // "Choose a Model" must never leave the dropdown empty, otherwise the request would silently fall back to the best model.
  useEffect(() => {
    if (mode === 'specific' && !model && availableModels[0]) setModel(availableModels[0].id)
  }, [mode, model, availableModels])

  const value = useMemo<ModelSelection>(
    () => ({
      mode,
      model,
      setMode,
      setModel,
      availableModels,
      defaultModelId,
      activeModelId: mode === 'best' ? defaultModelId : model || null,
      loading,
      error,
    }),
    [mode, model, availableModels, defaultModelId, loading, error],
  )

  return <ModelSelectionContext.Provider value={value}>{children}</ModelSelectionContext.Provider>
}

export function useModelSelection() {
  const context = useContext(ModelSelectionContext)
  if (!context) throw new Error('useModelSelection must be used inside ModelSelectionProvider')
  return context
}
