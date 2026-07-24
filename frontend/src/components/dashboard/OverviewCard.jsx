import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database } from 'lucide-react';

export default function OverviewCard({ icon: Icon, label, value, sub, source, details, isLoading }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    if (!isLoading && details && details.length > 0) {
      setIsExpanded((prev) => !prev);
    }
  };

  return (
    <div
      className={`bg-white border transition-all ${details && details.length > 0 ? 'cursor-pointer' : ''}`}
      style={{
        borderColor: 'var(--color-border)',
        boxShadow: 'var(--shadow-soft)',
        borderRadius: '10px',
      }}
      onClick={toggleExpand}
      onMouseEnter={(e) => { if (details?.length) e.currentTarget.style.borderColor = 'var(--color-blue)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; }}
    >
      <div className="p-5 space-y-3">
        {/* Label row */}
        <div className="flex items-start justify-between">
          <span
            className="text-[11px] font-semibold uppercase tracking-widest"
            style={{ color: 'var(--color-text-faint)', letterSpacing: '0.08em' }}
          >
            {label}
          </span>
          <div className="flex items-center gap-1.5">
            {!isLoading && Icon && (
              <Icon className="w-4 h-4 shrink-0" style={{ color: 'var(--color-blue)' }} />
            )}
            {details?.length > 0 && !isLoading && (
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); toggleExpand(); }}
                className="p-0.5 transition-colors"
                style={{ color: 'var(--color-text-faint)' }}
              >
                {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
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
        {!isLoading && sub && (
          <p
            className="text-xs leading-relaxed border-t pt-2"
            style={{ color: 'var(--color-text-faint)', borderColor: 'var(--color-border-light)' }}
          >
            {sub}
          </p>
        )}

        {/* Source */}
        {!isLoading && source && (
          <div className="flex items-center gap-1.5 text-[11px] font-mono" style={{ color: 'var(--color-text-faint)' }}>
            <Database className="w-3 h-3 shrink-0" />
            <span className="truncate">{source}</span>
          </div>
        )}
      </div>

      {/* Expanded details */}
      {isExpanded && !isLoading && details?.length > 0 && (
        <div
          className="border-t p-4 space-y-2 text-xs"
          style={{
            backgroundColor: 'var(--color-bg)',
            borderColor: 'var(--color-border-light)',
            borderRadius: '0 0 10px 10px',
          }}
        >
          <p className="font-semibold uppercase tracking-wide text-[10px]" style={{ color: 'var(--color-text-faint)' }}>
            Domain Breakdown
          </p>
          <div className="space-y-1.5">
            {details.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between" style={{ color: 'var(--color-text-muted)' }}>
                <span style={{ color: 'var(--color-text-faint)' }}>{item.label}</span>
                <span className="font-semibold" style={{ color: 'var(--color-text)' }}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
