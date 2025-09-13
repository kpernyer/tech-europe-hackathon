/**
 * Fine-tuning Experiment Component
 * Type-safe React component with proper error handling and separation of concerns
 */

import React, { useState, useCallback, useEffect } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { useAuth } from '../auth/AuthProvider'
import { useFineTuning } from '../../hooks/useFineTuning'
import type { Organization } from '../../types/fine-tuning'
import { ErrorBoundary } from '../../components/ErrorBoundary'
import { LoadingSpinner } from '../../components/LoadingSpinner'
import { Alert } from '../../components/Alert'

interface FineTuningExperimentProps {
  readonly className?: string
}

const FineTuningExperiment: React.FC<FineTuningExperimentProps> = ({ 
  className = '' 
}) => {
  const { getTenantId } = useAuth()
  const tenantId = getTenantId?.() ?? 'experiment-tenant'
  
  const {
    organizations,
    activeOrganization,
    isLoading,
    error,
    comparisonResults,
    setActiveOrganization,
    uploadDocument,
    generateTrainingData,
    startTraining,
    compareModels,
    clearError,
    refreshOrganizationStatus
  } = useFineTuning(tenantId)

  // Local form state
  const [uploadForm, setUploadForm] = useState({
    file: null as File | null,
    title: ''
  })
  const [comparisonQuery, setComparisonQuery] = useState(
    'What is our strategic vision for the next 5 years?'
  )

  const currentOrg = organizations.find(org => org.id === activeOrganization)

  // Refresh status periodically
  useEffect(() => {
    const interval = setInterval(() => {
      organizations.forEach(org => {
        if (org.modelStatus === 'training') {
          refreshOrganizationStatus(org.id)
        }
      })
    }, 10000) // Every 10 seconds

    return () => clearInterval(interval)
  }, [organizations, refreshOrganizationStatus])

  const handleFileSelect = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadForm(prev => ({
        file,
        title: prev.title || file.name.replace(/\.[^/.]+$/, '')
      }))
    }
  }, [])

  const handleUpload = useCallback(async (event: FormEvent) => {
    event.preventDefault()
    
    if (!uploadForm.file || !currentOrg) {
      return
    }

    const success = await uploadDocument({
      organizationId: activeOrganization,
      file: uploadForm.file,
      title: uploadForm.title
    })

    if (success) {
      setUploadForm({ file: null, title: '' })
      // Reset file input
      const fileInput = document.getElementById('fileInput') as HTMLInputElement
      if (fileInput) {
        fileInput.value = ''
      }
    }
  }, [uploadForm, currentOrg, activeOrganization, uploadDocument])

  const handleGenerateTrainingData = useCallback(async () => {
    await generateTrainingData(activeOrganization)
  }, [activeOrganization, generateTrainingData])

  const handleStartTraining = useCallback(async () => {
    await startTraining(activeOrganization)
  }, [activeOrganization, startTraining])

  const handleCompareModels = useCallback(async () => {
    await compareModels(comparisonQuery, organizations.map(org => org.id))
  }, [comparisonQuery, organizations, compareModels])

  const getStatusColor = (status: Organization['modelStatus']): string => {
    switch (status) {
      case 'ready': return 'bg-green-100 text-green-800'
      case 'training': return 'bg-yellow-100 text-yellow-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (!currentOrg) {
    return (
      <Alert 
        type="error" 
        title="Organization Not Found"
        message="The selected organization could not be found."
      />
    )
  }

  return (
    <div className={`max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 ${className}`}>
      <div className="px-4 py-6 sm:px-0">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Fine-tuning Experiment</h1>
          <p className="mt-2 text-gray-600">
            Compare organizational AI models trained on different company documents
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert 
            type="error"
            title={`Error: ${error.code}`}
            message={error.message}
            onClose={clearError}
            className="mb-6"
          />
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="mb-6">
            <LoadingSpinner message="Processing request..." />
          </div>
        )}

        {/* Organization Selector */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" role="tablist">
              {organizations.map((org) => (
                <button
                  key={org.id}
                  onClick={() => setActiveOrganization(org.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeOrganization === org.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                  role="tab"
                  aria-selected={activeOrganization === org.id}
                >
                  {org.name}
                  <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(org.modelStatus)}`}>
                    {org.modelStatus.replace('_', ' ')}
                  </span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Document Upload Section */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Upload Documents for {currentOrg.name}
              </h3>
              
              <form onSubmit={handleUpload} className="space-y-4">
                <div>
                  <label 
                    htmlFor="documentTitle" 
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Document Title
                  </label>
                  <input
                    id="documentTitle"
                    type="text"
                    value={uploadForm.title}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Strategic Plan 2024, Values Document, etc."
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  />
                </div>
                
                <div>
                  <label 
                    htmlFor="fileInput" 
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    File Upload
                  </label>
                  <input
                    id="fileInput"
                    type="file"
                    accept=".pdf,.docx,.doc,.txt,.md"
                    onChange={handleFileSelect}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                  />
                </div>

                {uploadForm.file && (
                  <div className="p-3 bg-gray-50 rounded-md">
                    <strong>{uploadForm.file.name}</strong> ({(uploadForm.file.size / 1024).toFixed(1)} KB)
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!uploadForm.file || isLoading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {isLoading ? 'Uploading...' : `Upload for ${currentOrg.name}`}
                </button>
              </form>

              {/* Documents List */}
              {currentOrg.documents.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">
                    Uploaded Documents ({currentOrg.documents.length})
                  </h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {currentOrg.documents.map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                        <div className="min-w-0 flex-1">
                          <div className="font-medium text-sm truncate">{doc.title}</div>
                          <div className="text-xs text-gray-500">
                            {doc.filename} • {(doc.size / 1024).toFixed(1)} KB
                          </div>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full flex-shrink-0 ml-2 ${
                          doc.processed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {doc.processed ? 'Processed' : 'Processing'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Training Control Section */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Model Training
              </h3>
              
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-md">
                  <h4 className="font-medium text-sm mb-2">{currentOrg.name} Status</h4>
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(currentOrg.modelStatus)}`}>
                      {currentOrg.modelStatus.replace('_', ' ')}
                    </span>
                    <span className="text-sm text-gray-600">
                      {currentOrg.documents.length} documents uploaded
                    </span>
                  </div>
                </div>

                <button
                  onClick={handleGenerateTrainingData}
                  disabled={isLoading || currentOrg.documents.length === 0}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {isLoading ? 'Generating...' : 'Generate Training Data'}
                </button>

                <button
                  onClick={handleStartTraining}
                  disabled={currentOrg.modelStatus === 'training' || isLoading}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {currentOrg.modelStatus === 'training' ? 'Training in Progress...' : 'Start Fine-tuning'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Model Comparison Section */}
        <div className="mt-8 bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Model Comparison
            </h3>
            
            <div className="space-y-4">
              <div>
                <label 
                  htmlFor="comparisonQuery" 
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Test Query
                </label>
                <textarea
                  id="comparisonQuery"
                  value={comparisonQuery}
                  onChange={(e) => setComparisonQuery(e.target.value)}
                  rows={3}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Enter a strategic question to test different models..."
                />
              </div>
              
              <button
                onClick={handleCompareModels}
                disabled={isLoading}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                {isLoading ? 'Comparing...' : 'Compare All Models'}
              </button>

              {comparisonResults && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-6">
                  <div className="p-4 border rounded-md">
                    <h4 className="font-medium text-sm mb-2">RAG Only (Baseline)</h4>
                    <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded whitespace-pre-wrap">
                      {comparisonResults.ragOnly}
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-md">
                    <h4 className="font-medium text-sm mb-2">{organizations[0].name} (Fine-tuned)</h4>
                    <div className="text-sm text-gray-700 bg-blue-50 p-3 rounded whitespace-pre-wrap">
                      {comparisonResults.fineTunedModels.org1}
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-md">
                    <h4 className="font-medium text-sm mb-2">{organizations[1].name} (Fine-tuned)</h4>
                    <div className="text-sm text-gray-700 bg-green-50 p-3 rounded whitespace-pre-wrap">
                      {comparisonResults.fineTunedModels.org2}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Export with error boundary
const FineTuningExperimentWithErrorBoundary: React.FC<FineTuningExperimentProps> = (props) => (
  <ErrorBoundary fallback={
    <Alert 
      type="error"
      title="Component Error"
      message="The fine-tuning experiment component encountered an error. Please refresh the page."
    />
  }>
    <FineTuningExperiment {...props} />
  </ErrorBoundary>
)

export default FineTuningExperimentWithErrorBoundary