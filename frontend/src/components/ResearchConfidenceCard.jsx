import React from 'react';
import { ShieldCheck, ExternalLink, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

export default function ResearchConfidenceCard({ scoreObj, metadata }) {
  if (!scoreObj) return null;

  const confPercent = scoreObj?.confidence_score ?? 0;
  const breakdown = scoreObj?.confidence_breakdown?.sources || {};

  const getBadge = (status) => {
    switch (status) {
      case 'Strong':
        return (
          <span
            className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded border"
            style={{ backgroundColor: '#f0fdfb', color: 'var(--color-teal)', borderColor: 'var(--color-teal-dim)' }}
          >
            <CheckCircle2 className="w-3 h-3" style={{ color: 'var(--color-teal)' }} /> Strong
          </span>
        );
      case 'Moderate':
        return (
          <span
            className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded border"
            style={{ backgroundColor: '#eff4ff', color: 'var(--color-blue)', borderColor: 'var(--color-blue-light)' }}
          >
            <CheckCircle2 className="w-3 h-3" style={{ color: 'var(--color-blue)' }} /> Moderate
          </span>
        );
      case 'Limited':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded border bg-amber-50 text-amber-700 border-amber-200">
            <AlertTriangle className="w-3 h-3 text-amber-600" /> Limited
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded border bg-rose-50 text-rose-700 border-rose-200">
            <XCircle className="w-3 h-3 text-rose-600" /> Unavailable
          </span>
        );
    }
  };

  const sourcesList = [
    { key: 'clinical',    label: 'Clinical Trials',       info: breakdown.clinical },
    { key: 'literature',  label: 'Scientific Literature',  info: breakdown.literature },
    { key: 'patent',      label: 'Patent Landscape',       info: breakdown.patent },
    { key: 'market',      label: 'Market Intelligence',    info: breakdown.market },
  ];

  return (
    <div
      className="bg-white border rounded-xl p-6 space-y-4"
      style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)' }}
    >
      {/* Header */}
      <div
        className="flex justify-between items-center border-b pb-4"
        style={{ borderColor: 'var(--color-border-light)' }}
      >
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5" style={{ color: 'var(--color-blue)' }} />
          <h3 className="text-base font-semibold" style={{ color: 'var(--color-text)' }}>
            Research Confidence &amp; Evidence Availability
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium" style={{ color: 'var(--color-text-faint)' }}>
            Confidence Score
          </span>
          <span
            className="text-xl font-bold tabular-nums"
            style={{ color: 'var(--color-text)' }}
          >
            {confPercent.toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Source matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {sourcesList.map((s) => {
          const status = s.info?.status || 'Unavailable';
          const name   = s.info?.source_name || s.label;
          const url    = s.info?.url || '#';

          return (
            <div
              key={s.key}
              className="p-3.5 rounded-xl border flex justify-between items-center"
              style={{ backgroundColor: 'var(--color-bg)', borderColor: 'var(--color-border-light)' }}
            >
              <div>
                <span
                  className="text-xs font-bold block"
                  style={{ color: 'var(--color-text)' }}
                >
                  {s.label}
                </span>
                <a
                  href={url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs hover:underline inline-flex items-center gap-1 mt-0.5 font-medium"
                  style={{ color: 'var(--color-blue)' }}
                >
                  {name}
                  <ExternalLink className="w-3 h-3" style={{ color: 'var(--color-blue)' }} />
                </a>
              </div>
              <div>{getBadge(status)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
