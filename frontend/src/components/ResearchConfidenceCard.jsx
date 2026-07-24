import React from 'react';
import { ShieldCheck, ExternalLink, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

export default function ResearchConfidenceCard({ scoreObj, metadata }) {
  if (!scoreObj) return null;

  const confPercent = scoreObj?.confidence_score ?? 0;
  const breakdown = scoreObj?.confidence_breakdown?.sources || {};

  const getBadge = (status) => {
    switch (status) {
      case 'Strong':
        return <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200"><CheckCircle2 className="w-3 h-3 text-emerald-600" /> ✓ Strong</span>;
      case 'Moderate':
        return <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200"><CheckCircle2 className="w-3 h-3 text-blue-600" /> ✓ Moderate</span>;
      case 'Limited':
        return <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200"><AlertTriangle className="w-3 h-3 text-amber-600" /> ✓ Limited</span>;
      default:
        return <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200"><XCircle className="w-3 h-3 text-rose-600" /> ❌ Unavailable</span>;
    }
  };

  const sourcesList = [
    { key: 'clinical', label: 'Clinical Trials', info: breakdown.clinical },
    { key: 'literature', label: 'Scientific Literature', info: breakdown.literature },
    { key: 'patent', label: 'Patent Landscape', info: breakdown.patent },
    { key: 'market', label: 'Market Intelligence', info: breakdown.market },
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4 my-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-indigo-600" />
          <h3 className="text-base font-bold text-slate-900">Research Confidence & Evidence Availability</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Confidence Score</span>
          <span className="text-xl font-extrabold text-slate-900">{confPercent.toFixed(0)}%</span>
        </div>
      </div>

      {/* Source Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {sourcesList.map((s) => {
          const status = s.info?.status || 'Unavailable';
          const name = s.info?.source_name || s.label;
          const url = s.info?.url || '#';

          return (
            <div key={s.key} className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <div>
                <span className="text-xs font-bold text-slate-700 block">{s.label}</span>
                <a
                  href={url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-indigo-600 hover:underline inline-flex items-center gap-1 mt-0.5 font-medium"
                >
                  {name}
                  <ExternalLink className="w-3 h-3 text-indigo-500" />
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
