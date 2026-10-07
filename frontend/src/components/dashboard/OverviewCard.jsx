import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database } from 'lucide-react';

export default function OverviewCard({ icon: Icon, label, value, sub, source, provenance, details, isLoading }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    if (!isLoading && details && details.length > 0) {
      setIsExpanded((prev) => !prev);
    }
  };

  // Honest display: If provenance is simulated, never display legal conclusions like "Free to Operate"
  let cleanSub = sub;
  if (provenance === 'simulated' && cleanSub) {
    cleanSub = cleanSub.replace(/Free to Operate[^\.]*/gi, 'Simulated landscape — unverified status');
  }

  // Filter details for simulated cards to avoid legal-sounding facts
  const cleanDetails = details?.map((item) => {
    if (provenance === 'simulated' && typeof item.value === 'string' && item.value.toLowerCase().includes('free to operate')) {
      return { ...item, value: 'Simulated data (unverified)' };
    }
    return item;
  });

  return (
    <div
      className={`bg-white border transition-all ${details && details.length > 0 ? 'cursor-pointer' : ''}`}
      style={{
        borderColor: 'var(--color-border-light)',
        boxShadow: 'var(--shadow-card)',
        borderRadius: '10px',
      }}
      onClick={toggleExpand}
      onMouseEnter={(e) => { if (details?.length) e.currentTarget.style.borderColor = 'var(--color-blue)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-light)'; }}
    >
      <div className="p-5 space-y-3">
        {/* Label row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span
              className="text-[11px] font-semibold uppercase tracking-wider"
              style={{ color: 'var(--color-text-faint)', letterSpacing: '0.06em' }}
            >
              {label}
            </span>
            {/* Provenance badge */}
            {!isLoading && provenance && (
              <span
                className="text-[10px] font-medium px-1.5 py-0.5 rounded border"
                style={
                  provenance === 'real'
                    ? { backgroundColor: '#f0fdfb', borderColor: 'var(--color-teal-dim)', color: 'var(--color-teal)' }
                    : provenance === 'simulated'
                    ? { backgroundColor: '#fffbeb', borderColor: '#fde68a', color: '#b45309' }
                    : { backgroundColor: '#f3f4f6', borderColor: '#e5e7eb', color: '#6b7280' }
                }
              >
                {provenance === 'real' ? 'Verified' : provenance === 'simulated' ? 'Simulated data' : 'Unavailable'}
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5">
            {!isLoading && Icon && (
              <Icon className="w-4 h-4 shrink-0" style={{ color: 'var(--color-blue)' }} />
            )}
            {details?.length > 0 && !isLoading && (
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); toggleExpand(); }}
                className="p-1 transition-colors rounded hover:bg-gray-100 cursor-pointer"
                style={{ color: 'var(--color-text-faint)' }}
                aria-label={isExpanded ? 'Collapse breakdown' : 'Expand breakdown'}
              >
                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            )}
          </div>
        </div>

        {/* Value */}
        {isLoading ? (
          <div className="space-y-1.5">
            <div className="h-8 w-28 bg-gray-100 animate-pulse" style={{ borderRadius: '4px' }} />
            <div className="h-3 w-36 bg-gray-100 animate-pulse" style={{ borderRadius: '4px' }} />
          </div>
        ) : (
          <p
            className="text-2xl font-semibold leading-none tabular-nums"
            style={{ color: 'var(--color-text)', letterSpacing: '-0.01em' }}
          >
            {value ?? '—'}
          </p>
        )}

        {/* Sub */}
        {!isLoading && cleanSub && (
          <p
            className="text-xs leading-relaxed border-t pt-2"
            style={{ color: 'var(--color-text-muted)', borderColor: 'var(--color-border-light)' }}
          >
            {cleanSub}
          </p>
        )}

        {/* Source - readable sans typography */}
        {!isLoading && source && (
          <div className="flex items-center gap-1.5 text-xs text-gray-500 pt-0.5">
            <Database className="w-3.5 h-3.5 shrink-0 text-gray-400" />
            <span className="truncate">{source}</span>
          </div>
        )}
      </div>

      {/* Expanded details */}
      {isExpanded && !isLoading && cleanDetails?.length > 0 && (
        <div
          className="border-t p-4 space-y-2.5 text-xs"
          style={{
            backgroundColor: '#fafbfc',
            borderColor: 'var(--color-border-light)',
            borderRadius: '0 0 10px 10px',
          }}
        >
          <p className="font-semibold uppercase tracking-wider text-[10px]" style={{ color: 'var(--color-text-faint)' }}>
            Domain Metric Breakdown
          </p>
          <div className="space-y-2">
            {cleanDetails.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between" style={{ color: 'var(--color-text-muted)' }}>
                <span style={{ color: 'var(--color-text-faint)' }}>{item.label}</span>
                <span className="font-medium" style={{ color: 'var(--color-text)' }}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
