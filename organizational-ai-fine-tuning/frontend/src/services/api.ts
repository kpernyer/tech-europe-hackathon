/**
 * Fine-tuning Service
 * Type-safe API layer with proper error handling and fallbacks
 */

import type {
  Organization,
  UploadRequest,
  UploadResponse,
  TrainingDataRequest,
  TrainingDataResponse,
  ComparisonRequest,
  ModelComparisonResults,
  OrganizationStatus,
  ApiResponse,
  ApiError
} from '../types/fine-tuning'

import { apiFetch } from '../shared/api'

class FineTuningServiceImpl {
  private readonly baseUrl = '/experiments/fine-tuning'

  /**
   * Upload document for organization
   */
  async uploadDocument(request: UploadRequest): Promise<ApiResponse<UploadResponse>> {
    try {
      const formData = new FormData()
      formData.append('file', request.file)
      formData.append('title', request.title)
      formData.append('organization_id', request.organizationId)
      formData.append('tenantId', request.tenantId)

      const response = await apiFetch(`${this.baseUrl}/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        return {
          success: false,
          error: {
            code: 'UPLOAD_FAILED',
            message: errorData.detail || 'Upload failed',
            details: errorData
          }
        }
      }

      const data = await response.json()
      return {
        success: true,
        data: {
          documentId: data.document_id,
          message: data.message,
          fileType: data.file_type,
          size: data.size
        }
      }
    } catch (error) {
      return this.handleError('UPLOAD_ERROR', error)
    }
  }

  /**
   * Generate training data from uploaded documents
   */
  async generateTrainingData(request: TrainingDataRequest): Promise<ApiResponse<TrainingDataResponse>> {
    try {
      const response = await apiFetch(`${this.baseUrl}/generate-training-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          organization_id: request.organizationId,
          tenantId: request.tenantId
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        return {
          success: false,
          error: {
            code: 'TRAINING_DATA_FAILED',
            message: errorData.detail || 'Failed to generate training data',
            details: errorData
          }
        }
      }

      const data = await response.json()
      return {
        success: true,
        data: {
          examples: data.examples || [],
          totalCount: data.total_count || 0,
          trainingFile: data.training_file || ''
        }
      }
    } catch (error) {
      return this.handleError('TRAINING_DATA_ERROR', error)
    }
  }

  /**
   * Start fine-tuning process
   */
  async startTraining(request: TrainingDataRequest): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiFetch(`${this.baseUrl}/start-training`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          organization_id: request.organizationId,
          tenantId: request.tenantId
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        return {
          success: false,
          error: {
            code: 'TRAINING_START_FAILED',
            message: errorData.detail || 'Failed to start training',
            details: errorData
          }
        }
      }

      const data = await response.json()
      return {
        success: true,
        data: { message: data.message }
      }
    } catch (error) {
      return this.handleError('TRAINING_START_ERROR', error)
    }
  }

  /**
   * Compare models with query
   */
  async compareModels(request: ComparisonRequest): Promise<ApiResponse<ModelComparisonResults>> {
    try {
      const response = await apiFetch(`${this.baseUrl}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: request.query,
          organizations: request.organizations,
          tenantId: request.tenantId
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        return {
          success: false,
          error: {
            code: 'COMPARISON_FAILED',
            message: errorData.detail || 'Model comparison failed',
            details: errorData
          }
        }
      }

      const data = await response.json()
      return {
        success: true,
        data: {
          ragOnly: data.rag_only || 'No RAG response available',
          fineTunedModels: {
            org1: data.fine_tuned_org1 || 'Model not ready',
            org2: data.fine_tuned_org2 || 'Model not ready'
          }
        }
      }
    } catch (error) {
      return this.handleError('COMPARISON_ERROR', error)
    }
  }

  /**
   * Get organization training status
   */
  async getOrganizationStatus(organizationId: string): Promise<ApiResponse<OrganizationStatus>> {
    try {
      const response = await apiFetch(`${this.baseUrl}/status/${organizationId}`)

      if (!response.ok) {
        // Return dummy data instead of failing
        return {
          success: true,
          data: {
            organizationId,
            status: 'not_started',
            documentsCount: 0,
            trainingExamples: 0
          }
        }
      }

      const data = await response.json()
      return {
        success: true,
        data: {
          organizationId: data.organization_id,
          status: data.status,
          documentsCount: data.documents_count,
          trainingExamples: data.training_examples,
          modelPath: data.model_path
        }
      }
    } catch (error) {
      // Fallback to dummy data
      return {
        success: true,
        data: {
          organizationId,
          status: 'not_started',
          documentsCount: 0,
          trainingExamples: 0
        }
      }
    }
  }

  private handleError(code: string, error: unknown): ApiResponse<never> {
    const message = error instanceof Error ? error.message : 'Unknown error occurred'
    
    console.error(`FineTuningService Error [${code}]:`, error)
    
    return {
      success: false,
      error: {
        code,
        message,
        details: error instanceof Error ? { stack: error.stack } : { error }
      }
    }
  }
}

// Export singleton instance
export const fineTuningService = new FineTuningServiceImpl()
export type FineTuningService = FineTuningServiceImpl