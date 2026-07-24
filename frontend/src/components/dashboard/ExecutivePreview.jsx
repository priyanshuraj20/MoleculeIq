import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, ArrowRight } from 'lucide-react';

/**
 * ExecutivePreview — Stitch-styled executive summary card.
 */
export default function ExecutivePreview({ sections, summary, moleculeName, isLoading }) {
  const reportUrl = `/report?q=${encodeURIComponent(moleculeName || 'Metformin')}`;

  return (
    <div
      className="bg-white rounded-xl border p-6 space-y-5 flex flex-col"
      style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)' }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-0.5">
          <h2 className="text-base font-semibold" style={{ color: 'var(--color-text)' }}>
            Executive Summary
          </h2>
          <p className="text-xs" style={{ color: 'var(--color-text-faint)' }}>
            Strategic intelligence synthesized across all research domains.
          </p>
        </div>
        <div
          className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border-light)' }}
        >
          <FileText className="w-4 h-4" style={{ color: 'var(--color-text-muted)' }} />
        </div>
      </div>

      <div className="border-t" style={{ borderColor: 'var(--color-border-light)' }} />

      {/* Content */}
      <div className="space-y-4 flex-grow">
        {isLoading ? (
          <>
            <div className="space-y-2">
              {[100, 90, 95, 80].map((w, i) => (
                <div key={i} className="h-3 bg-gray-100 rounded animate-pulse" style={{ width: `${w}%` }} />
              ))}
            </div>
            <div className="space-y-2 pt-2">
              {[95, 85, 100].map((w, i) => (
                <div key={i} className="h-3 bg-gray-100 rounded animate-pulse" style={{ width: `${w}%` }} />
              ))}
            </div>
          </>
        ) : sections && sections.length > 0 ? (
          <div className="space-y-3">
            {sections.map(({ title, icon: Icon, content }) => (
              <div
                key={title}
                className="p-3.5 rounded-lg border space-y-1.5"
                style={{ backgroundColor: 'var(--color-bg)', borderColor: 'var(--color-border-light)' }}
              >
                <div
                  className="flex items-center gap-2 text-xs font-semibold"
                  style={{ color: 'var(--color-text)' }}
                >
                  {Icon && <Icon className="w-3.5 h-3.5 shrink-0" style={{ color: 'var(--color-blue)' }} />}
                  <span>{title}</span>
                </div>
                <p className="text-xs leading-relaxed pl-5" style={{ color: 'var(--color-text-muted)' }}>
                  {content}
                </p>
              </div>
            ))}
          </div>
        ) : summary ? (
          summary.split('\n\n').filter(Boolean).map((para, i) => (
            <p key={i} className="text-sm leading-relaxed" style={{ color: 'var(--color-text-muted)' }}>
              {para.trim()}
            </p>
          ))
        ) : (
          <p className="text-sm" style={{ color: 'var(--color-text-faint)' }}>
            Run a search to generate the executive summary for this molecule.
          </p>
        )}
      </div>

      {/* CTA */}
      <div className="pt-2 border-t" style={{ borderColor: 'var(--color-border-light)' }}>
        <Link
          to={reportUrl}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white rounded-lg transition-all shadow-sm"
          style={{ backgroundColor: 'var(--color-blue)' }}
          onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-blue-hover)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-blue)'; }}
        >
          <FileText className="w-4 h-4" />
          View Full Executive Report
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
