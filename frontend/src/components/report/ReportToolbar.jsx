import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Download, FileText, Clock, Loader2 } from 'lucide-react';

/**
 * ReportToolbar
 * Sticky top navigation toolbar for Executive Report Workspace.
 * Features live PDF export trigger button with active loading & aria accessibility states.
 *
 * Props:
 *   moleculeName   string
 *   generatedTime  string
 *   onDownloadPdf  () => void — triggers backend PDF generation
 *   isDownloading  boolean — disables button and shows progress spinner
 */
export default function ReportToolbar({
  moleculeName,
  generatedTime,
  onDownloadPdf,
  isDownloading,
}) {
  return (
    <div className="sticky top-16 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm py-3 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        {/* Left: Back Link & Molecule Title */}
        <div className="flex items-center gap-4">
          <Link
            to="/research"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            aria-label="Back to Research Dashboard"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Dashboard
          </Link>
          <div className="h-4 w-px bg-slate-200 hidden sm:block" />
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-indigo-600 shrink-0" />
            <h1 className="text-base font-bold text-slate-900 tracking-tight">
              {moleculeName ? `${moleculeName} Executive Research Report` : 'Executive Research Report'}
            </h1>
          </div>
        </div>

        {/* Right: Timestamp & PDF Download Button */}
        <div className="flex items-center gap-3 text-xs shrink-0 w-full sm:w-auto justify-between sm:justify-end">
          {generatedTime && (
            <div className="flex items-center gap-1.5 text-slate-400">
              <Clock className="w-3.5 h-3.5" />
              <span>{generatedTime}</span>
            </div>
          )}

          <button
            id="download-pdf-button"
            type="button"
            onClick={onDownloadPdf}
            disabled={isDownloading || !moleculeName}
            aria-label={isDownloading ? 'Preparing PDF report' : 'Download Executive Report PDF'}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 rounded-lg transition-colors shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isDownloading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Preparing PDF...</span>
              </>
            ) : (
              <>
                <Download className="w-3.5 h-3.5" />
                <span>Download PDF</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
