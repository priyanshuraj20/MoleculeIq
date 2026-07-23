import React from 'react';
import { Search, FlaskConical } from 'lucide-react';

export default function ResearchPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
          Pharmaceutical Research Portal
        </h1>
        <p className="text-slate-600 text-sm">
          Search target molecules to orchestrate real-time multi-agent research pipelines.
        </p>
      </div>

      {/* Search Input Placeholder Box */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-grow">
            <Search className="w-5 h-5 absolute left-3.5 top-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Enter molecule name (e.g. Metformin, Ibuprofen)..."
              className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white text-sm"
              disabled
            />
          </div>
          <button
            disabled
            className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg opacity-80 cursor-not-allowed text-sm flex items-center justify-center gap-2"
          >
            <FlaskConical className="w-4 h-4" />
            Run Research
          </button>
        </div>
        <div className="text-xs text-slate-500 flex items-center gap-2">
          <span>Sample queries:</span>
          <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 font-mono">Metformin</span>
          <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 font-mono">Ibuprofen</span>
        </div>
      </div>

      {/* Placeholder Notice */}
      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-8 text-center space-y-3">
        <div className="w-12 h-12 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center mx-auto">
          <FlaskConical className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-semibold text-indigo-950">
          Research Portal Dashboard Placeholder
        </h3>
        <p className="text-indigo-700 text-sm max-w-md mx-auto">
          Full interactive SSE streaming, scoring metrics, domain tab visualizations, and PDF downloads will be integrated in Session 18.
        </p>
      </div>
    </div>
  );
}
