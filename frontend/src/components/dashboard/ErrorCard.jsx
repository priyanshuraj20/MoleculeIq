import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

/**
 * ErrorCard
 * Shown when the research pipeline returns an error.
 *
 * Props:
 *   message  string  — human-friendly error description
 *   onRetry  () => void — callback to retry
 */
export default function ErrorCard({ message, onRetry }) {
  return (
    <div className="bg-white rounded-xl border border-red-200 p-6 flex flex-col sm:flex-row items-start sm:items-center gap-4">
      <div className="shrink-0 w-10 h-10 rounded-lg bg-red-50 border border-red-100 flex items-center justify-center text-red-500">
        <AlertTriangle className="w-5 h-5" />
      </div>
      <div className="flex-grow space-y-1 min-w-0">
        <p className="text-sm font-semibold text-slate-900">Research Pipeline Error</p>
        <p className="text-xs text-slate-500 leading-relaxed break-words">
          {message ?? 'An unexpected error occurred. Please try again.'}
        </p>
      </div>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="shrink-0 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors focus:outline-none"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      )}
    </div>
  );
}
