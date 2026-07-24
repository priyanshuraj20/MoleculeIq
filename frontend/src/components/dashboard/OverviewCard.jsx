import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database } from 'lucide-react';

/**
 * OverviewCard
 * Summary metric card for one research domain with expandable detailed view.
 *
 * Props:
 *   icon        Lucide icon component
 *   label       domain name string
 *   value       primary metric string (e.g. "528 Trials")
 *   sub         optional secondary text
 *   source      data source string (e.g. "ClinicalTrials.gov API v2")
 *   details     array of { label, value } detail rows for expanded view
 *   isLoading   boolean — shows skeleton shimmer
 */
export default function OverviewCard({ icon: Icon, label, value, sub, source, details, isLoading }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    if (!isLoading && details && details.length > 0) {
      setIsExpanded((prev) => !prev);
    }
  };

  return (
    <div
      className={`bg-white rounded-xl border border-slate-200 transition-all ${
        details && details.length > 0 ? 'cursor-pointer hover:border-indigo-300' : ''
      }`}
      onClick={toggleExpand}
    >
      <div className="p-5 space-y-3">
        {/* Top Icon & Expand Arrow */}
        <div className="flex items-center justify-between">
          <div className="w-9 h-9 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
            <Icon className="w-4 h-4" />
          </div>
          {details && details.length > 0 && !isLoading && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                toggleExpand();
              }}
              className="text-slate-400 hover:text-slate-600 p-1 rounded-md transition-colors"
              aria-label="Toggle details"
            >
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          )}
        </div>

        {/* Metric */}
        <div>
          {isLoading ? (
            <>
              <div className="h-7 w-24 bg-slate-100 rounded animate-pulse mb-1" />
              <div className="h-3 w-32 bg-slate-100 rounded animate-pulse" />
            </>
          ) : (
            <>
              <p className="text-2xl font-bold text-slate-900 leading-none">{value ?? '—'}</p>
              <p className="text-xs font-medium text-slate-500 mt-1">{label}</p>
            </>
          )}
        </div>

        {/* Sub-text */}
        {!isLoading && sub && (
          <p className="text-xs text-slate-400 leading-relaxed border-t border-slate-100 pt-2">{sub}</p>
        )}

        {/* Source Transparency Badge (Feature 5) */}
        {!isLoading && source && (
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono pt-1">
            <Database className="w-3 h-3 text-slate-400 shrink-0" />
            <span className="truncate">{source}</span>
          </div>
        )}
      </div>

      {/* Expanded Details Panel (Feature 3) */}
      {isExpanded && !isLoading && details && details.length > 0 && (
        <div className="bg-slate-50/80 border-t border-slate-100 p-4 rounded-b-xl space-y-2 text-xs">
          <p className="font-semibold text-slate-500 uppercase tracking-wide text-[10px]">Domain Breakdown</p>
          <div className="space-y-1.5">
            {details.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-slate-600">
                <span className="text-slate-500">{item.label}</span>
                <span className="font-medium text-slate-900 text-right">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
