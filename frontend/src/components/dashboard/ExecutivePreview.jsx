import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, ArrowRight } from 'lucide-react';

/**
 * ExecutivePreview
 * Feature 4 — Executive Summary preview card with navigation to full Report Workspace.
 *
 * Props:
 *   sections      array of { title, icon, content } derived from backend ResearchContext
 *   summary       string raw fallback text
 *   moleculeName  string
 *   isLoading     boolean
 */
export default function ExecutivePreview({ sections, summary, moleculeName, isLoading }) {
  const reportUrl = `/report?q=${encodeURIComponent(moleculeName || 'Metformin')}`;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-5 flex flex-col">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-0.5">
          <h2 className="text-base font-semibold text-slate-900">Executive Summary</h2>
          <p className="text-xs text-slate-500">
            Strategic intelligence synthesized across all research domains.
          </p>
        </div>
        <div className="shrink-0 w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500">
          <FileText className="w-4 h-4" />
        </div>
      </div>

      <div className="border-t border-slate-100" />

      {/* Content */}
      <div className="space-y-4 flex-grow">
        {isLoading ? (
          <>
            <div className="space-y-2">
              {[100, 90, 95, 80].map((w, i) => (
                <div key={i} className="h-3 bg-slate-100 rounded animate-pulse" style={{ width: `${w}%` }} />
              ))}
            </div>
            <div className="space-y-2 pt-2">
              {[95, 85, 100].map((w, i) => (
                <div key={i} className="h-3 bg-slate-100 rounded animate-pulse" style={{ width: `${w}%` }} />
              ))}
            </div>
          </>
        ) : sections && sections.length > 0 ? (
          <div className="space-y-3.5">
            {sections.map(({ title, icon: Icon, content }) => (
              <div key={title} className="bg-slate-50/80 p-3.5 rounded-lg border border-slate-100 space-y-1.5">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-900">
                  {Icon && <Icon className="w-3.5 h-3.5 text-indigo-600 shrink-0" />}
                  <span>{title}</span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed pl-5">{content}</p>
              </div>
            ))}
          </div>
        ) : summary ? (
          summary.split('\n\n').filter(Boolean).map((para, i) => (
            <p key={i} className="text-sm text-slate-600 leading-relaxed">
              {para.trim()}
            </p>
          ))
        ) : (
          <p className="text-sm text-slate-400">
            Run a search to generate the executive summary for this molecule.
          </p>
        )}
      </div>

      {/* CTA Link to Full Executive Report Workspace (Session 21) */}
      <div className="pt-2 border-t border-slate-100">
        <Link
          to={reportUrl}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors shadow-sm"
        >
          <FileText className="w-4 h-4" />
          View Full Executive Report
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
