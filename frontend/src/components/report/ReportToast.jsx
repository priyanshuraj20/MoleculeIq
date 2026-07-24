import React from 'react';
import { CheckCircle2, AlertCircle, X, RefreshCw } from 'lucide-react';

/**
 * ReportToast
 * Subtle banner notification for success and error feedback without alert popups.
 *
 * Props:
 *   type     'success' | 'error'
 *   message  string
 *   onClose  () => void
 *   onRetry  () => void (optional for error)
 */
export default function ReportToast({ type = 'success', message, onClose, onRetry }) {
  if (!message) return null;

  const isSuccess = type === 'success';

  return (
    <div
      role="alert"
      className={`rounded-xl border p-4 shadow-sm flex items-start sm:items-center justify-between gap-3 transition-all ${
        isSuccess
          ? 'bg-emerald-50/90 border-emerald-200 text-emerald-900'
          : 'bg-red-50/90 border-red-200 text-red-900'
      }`}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        {isSuccess ? (
          <CheckCircle2 className="w-4.5 h-4.5 text-emerald-600 shrink-0" />
        ) : (
          <AlertCircle className="w-4.5 h-4.5 text-red-600 shrink-0" />
        )}
        <span className="text-xs sm:text-sm font-medium leading-normal break-words">
          {message}
        </span>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {!isSuccess && onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-red-700 bg-red-100 hover:bg-red-200 rounded-md transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        )}
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-md transition-colors"
            aria-label="Close notification"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
