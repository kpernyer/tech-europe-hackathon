/**
 * Fine-tuning Experiment Types
 * Type-safe definitions for the fine-tuning experiment system
 */

export interface Organization {
  readonly id: string
  readonly name: string
  readonly industry: string
  readonly documents: ReadonlyArray<Document>
  readonly modelStatus: ModelStatus
  readonly modelPath?: string
}

export interface Document {
  readonly id: string
  readonly filename: string
  readonly title: string
  readonly uploadedAt: string
  readonly size: number
  readonly processed: boolean
}

export interface TrainingExample {
  readonly instruction: string
  readonly input: string
  readonly output: string
  readonly sourceDoc: string
}

export interface ModelComparison {
  readonly query: string
  readonly results: ModelComparisonResults
  readonly timestamp: string
}

export interface ModelComparisonResults {
  readonly ragOnly: string
  readonly fineTunedModels: Record<string, string>
}

export type ModelStatus = 
  | 'not_started'
  | 'training' 
  | 'ready' 
  | 'error'

export interface UploadRequest {
  readonly organizationId: string
  readonly tenantId: string
  readonly file: File
  readonly title: string
}

export interface TrainingDataRequest {
  readonly organizationId: string
  readonly tenantId: string
}

export interface ComparisonRequest {
  readonly query: string
  readonly organizations: ReadonlyArray<string>
  readonly tenantId: string
}

// API Response Types
export interface ApiResponse<T> {
  readonly success: boolean
  readonly data?: T
  readonly error?: ApiError
}

export interface ApiError {
  readonly code: string
  readonly message: string
  readonly details?: Record<string, unknown>
}

export interface UploadResponse {
  readonly documentId: string
  readonly message: string
  readonly fileType: string
  readonly size: number
}

export interface TrainingDataResponse {
  readonly examples: ReadonlyArray<TrainingExample>
  readonly totalCount: number
  readonly trainingFile: string
}

export interface OrganizationStatus {
  readonly organizationId: string
  readonly status: ModelStatus
  readonly documentsCount: number
  readonly trainingExamples: number
  readonly modelPath?: string
}