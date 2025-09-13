/**
 * Loading Spinner Component
 * Type-safe loading indicator with optional message
 */

import React from 'react'

interface LoadingSpinnerProps {
  readonly message?: string
  readonly size?: 'sm' | 'md' | 'lg'
  readonly className?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  size = 'md',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }

  return (
    <div className={`flex items-center justify-center space-x-3 ${className}`}>
      <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-indigo-600 ${sizeClasses[size]}`} />
      {message && (
        <span className="text-sm text-gray-600">{message}</span>
      )}
    </div>
  )
}