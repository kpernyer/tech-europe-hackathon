/**
 * Fine-tuning React Hooks
 * Type-safe state management with proper error handling
 */

import { useState, useCallback, useRef } from 'react'
import type {
  Organization,
  UploadRequest,
  TrainingDataRequest,
  ComparisonRequest,
  ModelComparisonResults,
  ApiError,
  ModelStatus
} from '../types/fine-tuning'

import { fineTuningService } from '../services/fine-tuning.service'

interface UseFineTuningState {
  readonly organizations: ReadonlyArray<Organization>
  readonly activeOrganization: string
  readonly isLoading: boolean
  readonly error: ApiError | null
  readonly comparisonResults: ModelComparisonResults | null
}

interface UseFineTuningActions {
  readonly setActiveOrganization: (orgId: string) => void
  readonly uploadDocument: (request: Omit<UploadRequest, 'tenantId'>) => Promise<boolean>
  readonly generateTrainingData: (organizationId: string) => Promise<boolean>
  readonly startTraining: (organizationId: string) => Promise<boolean>
  readonly compareModels: (query: string, organizations: ReadonlyArray<string>) => Promise<boolean>
  readonly clearError: () => void
  readonly refreshOrganizationStatus: (organizationId: string) => Promise<void>
}

export interface UseFineTuningReturn extends UseFineTuningState, UseFineTuningActions {}

export function useFineTuning(tenantId: string): UseFineTuningReturn {
  const [state, setState] = useState<UseFineTuningState>({
    organizations: [
      {
        id: 'org1',
        name: 'TechCorp Inc',
        industry: 'Technology',
        documents: [],
        modelStatus: 'not_started'
      },
      {
        id: 'org2',
        name: 'ManufacturingCo',
        industry: 'Manufacturing',
        documents: [],
        modelStatus: 'not_started'
      }
    ],
    activeOrganization: 'org1',
    isLoading: false,
    error: null,
    comparisonResults: null
  })

  // Use ref to prevent stale closure issues
  const stateRef = useRef(state)
  stateRef.current = state

  const updateState = useCallback((updates: Partial<UseFineTuningState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }, [])

  const setActiveOrganization = useCallback((orgId: string) => {
    updateState({ activeOrganization: orgId, error: null })
  }, [updateState])

  const uploadDocument = useCallback(async (
    request: Omit<UploadRequest, 'tenantId'>
  ): Promise<boolean> => {
    updateState({ isLoading: true, error: null })

    try {
      const result = await fineTuningService.uploadDocument({
        ...request,
        tenantId
      })

      if (result.success && result.data) {
        // Update organization documents
        updateState({
          organizations: stateRef.current.organizations.map(org =>
            org.id === request.organizationId
              ? {
                  ...org,
                  documents: [
                    ...org.documents,
                    {
                      id: result.data!.documentId,
                      filename: request.file.name,
                      title: request.title,
                      uploadedAt: new Date().toISOString(),
                      size: request.file.size,
                      processed: false
                    }
                  ]
                }
              : org
          ),
          isLoading: false
        })
        return true
      } else {
        updateState({ 
          error: result.error || { code: 'UNKNOWN', message: 'Upload failed' },
          isLoading: false 
        })
        return false
      }
    } catch (error) {
      updateState({
        error: {
          code: 'UPLOAD_ERROR',
          message: error instanceof Error ? error.message : 'Upload failed'
        },
        isLoading: false
      })
      return false
    }
  }, [tenantId, updateState])

  const generateTrainingData = useCallback(async (organizationId: string): Promise<boolean> => {
    updateState({ isLoading: true, error: null })

    try {
      const result = await fineTuningService.generateTrainingData({
        organizationId,
        tenantId
      })

      if (result.success) {
        updateState({ isLoading: false })
        return true
      } else {
        updateState({ 
          error: result.error || { code: 'UNKNOWN', message: 'Training data generation failed' },
          isLoading: false 
        })
        return false
      }
    } catch (error) {
      updateState({
        error: {
          code: 'TRAINING_DATA_ERROR',
          message: error instanceof Error ? error.message : 'Training data generation failed'
        },
        isLoading: false
      })
      return false
    }
  }, [tenantId, updateState])

  const startTraining = useCallback(async (organizationId: string): Promise<boolean> => {
    updateState({ isLoading: true, error: null })

    try {
      const result = await fineTuningService.startTraining({
        organizationId,
        tenantId
      })

      if (result.success) {
        // Update model status to training
        updateState({
          organizations: stateRef.current.organizations.map(org =>
            org.id === organizationId
              ? { ...org, modelStatus: 'training' as ModelStatus }
              : org
          ),
          isLoading: false
        })
        return true
      } else {
        updateState({ 
          error: result.error || { code: 'UNKNOWN', message: 'Training start failed' },
          isLoading: false 
        })
        return false
      }
    } catch (error) {
      updateState({
        error: {
          code: 'TRAINING_START_ERROR',
          message: error instanceof Error ? error.message : 'Training start failed'
        },
        isLoading: false
      })
      return false
    }
  }, [tenantId, updateState])

  const compareModels = useCallback(async (
    query: string,
    organizations: ReadonlyArray<string>
  ): Promise<boolean> => {
    updateState({ isLoading: true, error: null })

    try {
      const result = await fineTuningService.compareModels({
        query,
        organizations,
        tenantId
      })

      if (result.success && result.data) {
        updateState({ 
          comparisonResults: result.data,
          isLoading: false 
        })
        return true
      } else {
        updateState({ 
          error: result.error || { code: 'UNKNOWN', message: 'Model comparison failed' },
          isLoading: false 
        })
        return false
      }
    } catch (error) {
      updateState({
        error: {
          code: 'COMPARISON_ERROR',
          message: error instanceof Error ? error.message : 'Model comparison failed'
        },
        isLoading: false
      })
      return false
    }
  }, [tenantId, updateState])

  const refreshOrganizationStatus = useCallback(async (organizationId: string): Promise<void> => {
    try {
      const result = await fineTuningService.getOrganizationStatus(organizationId)
      
      if (result.success && result.data) {
        updateState({
          organizations: stateRef.current.organizations.map(org =>
            org.id === organizationId
              ? { ...org, modelStatus: result.data!.status }
              : org
          )
        })
      }
    } catch (error) {
      // Silently fail - this is just a status refresh
      console.warn('Failed to refresh organization status:', error)
    }
  }, [updateState])

  const clearError = useCallback(() => {
    updateState({ error: null })
  }, [updateState])

  return {
    ...state,
    setActiveOrganization,
    uploadDocument,
    generateTrainingData,
    startTraining,
    compareModels,
    clearError,
    refreshOrganizationStatus
  }
}