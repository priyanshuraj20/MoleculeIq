import React, { useState } from 'react';
import { Compass, Target, ExternalLink, ChevronDown, ChevronUp, FlaskConical, AlertCircle, FileText } from 'lucide-react';

export default function RepurposingCard({ repurposing, isLoading }) {
  const [expandedCandidate, setExpandedCandidate] = useState(0);

  const candidates = repurposing?.candidates || [];
  const provenance = repurposing?.provenance || 'real';

  return (
    <div
      className="bg-white rounded-xl border p-6 space-y-5 flex flex-col"
      style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)' }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <h2 className="text-base font-semibold" style={{ color: 'var(--color-text)' }}>
              Drug Repurposing Discovery
            </h2>
            <span
              className="text-xs font-medium px-2 py-0.5 rounded border"
              style={{
                backgroundColor: provenance === 'real' ? '#f0fdfb' : '#fffbeb',
                borderColor: provenance === 'real' ? 'var(--color-teal-dim)' : '#fde68a',
                color: provenance === 'real' ? 'var(--color-teal)' : '#b45309',
              }}
            >
              {provenance === 'real' ? 'Verified' : 'Simulated'}
            </span>
          </div>
          <p className="text-xs" style={{ color: 'var(--color-text-faint)' }}>
            Candidate new indications ranked by target association &amp; real clinical/scientific evidence.
          </p>
        </div>
        <div
          className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border-light)' }}
        >
          <Compass className="w-4 h-4" style={{ color: 'var(--color-blue)' }} />
        </div>
      </div>

      <div className="border-t" style={{ borderColor: 'var(--color-border-light)' }} />

      {/* Content */}
      <div className="space-y-3 flex-grow">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 rounded-lg border border-gray-100 bg-gray-50/50 space-y-2 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/3" />
                <div className="h-3 bg-gray-100 rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : candidates.length === 0 ? (
          <div className="p-6 text-center rounded-lg border border-dashed border-gray-200 space-y-2">
            <FlaskConical className="w-6 h-6 mx-auto text-gray-400" />
            <p className="text-sm font-medium text-gray-600">No repurposing candidates found</p>
            <p className="text-xs text-gray-400">
              No unapproved target-disease associations with actionable evidence were identified for this molecule.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {candidates.map((cand, idx) => {
              const isExpanded = expandedCandidate === idx;
              const hasEvidence = cand.evidence && cand.evidence.length > 0;

              return (
                <div
                  key={cand.disease_id || idx}
                  className="rounded-lg border transition-all"
                  style={{
                    backgroundColor: isExpanded ? 'var(--color-bg)' : '#ffffff',
                    borderColor: isExpanded ? 'var(--color-blue)' : 'var(--color-border-light)',
                  }}
                >
                  {/* Candidate Summary Header */}
                  <div
                    onClick={() => setExpandedCandidate(isExpanded ? null : idx)}
                    className="p-3.5 flex items-center justify-between gap-3 cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span
                        className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                        style={{
                          backgroundColor: idx === 0 ? '#eff4ff' : 'var(--color-bg)',
                          color: idx === 0 ? 'var(--color-blue)' : 'var(--color-text-muted)',
                          border: '1px solid var(--color-border-light)',
                        }}
                      >
                        {idx + 1}
                      </span>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold truncate" style={{ color: 'var(--color-text)' }}>
                            {cand.disease_name}
                          </span>
                          <span className="text-[11px] font-mono px-1.5 py-0.2 rounded bg-gray-100 text-gray-600">
                            {cand.disease_id}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-500 mt-0.5">
                          <span className="flex items-center gap-1">
                            <Target className="w-3 h-3 text-indigo-500" />
                            {cand.targets?.join(', ') || 'Target N/A'}
                          </span>
                          <span>•</span>
                          <span>
                            {cand.evidence_trials_count ?? 0} trials · {cand.evidence_papers_count ?? 0} papers
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-right">
                        <div className="text-xs font-semibold" style={{ color: 'var(--color-blue)' }}>
                          Score: {(cand.association_score ?? 0).toFixed(3)}
                        </div>
                        <div className="text-[10px] text-gray-400">Assoc. strength</div>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="px-3.5 pb-3.5 pt-1 space-y-3 border-t" style={{ borderColor: 'var(--color-border-light)' }}>
                      {/* Bounded Rationale */}
                      {cand.why_it_could_work && (
                        <div className="p-3 rounded-md bg-white border border-slate-200 space-y-1">
                          <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-700">
                            <FileText className="w-3.5 h-3.5 text-slate-500" />
                            <span>Biological Rationale / Mechanism Hypothesis</span>
                          </div>
                          <p className="text-xs text-gray-700 leading-relaxed">
                            {cand.why_it_could_work}
                          </p>
                        </div>
                      )}

                      {/* Real Evidence Items */}
                      <div>
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 mb-1.5">
                          Supporting Evidence Citations
                        </div>
                        {hasEvidence ? (
                          <div className="space-y-1.5">
                            {cand.evidence.map((ev, evIdx) => (
                              <a
                                key={ev.id || evIdx}
                                href={ev.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-start justify-between gap-2 p-2 rounded bg-white border border-gray-100 hover:border-blue-200 transition-colors group"
                              >
                                <div className="space-y-0.5 min-w-0">
                                  <div className="flex items-center gap-1.5">
                                    <span
                                      className={`text-[10px] font-bold uppercase px-1.5 py-0.2 rounded ${
                                        ev.type === 'trial'
                                          ? 'bg-blue-50 text-blue-700 border border-blue-100'
                                          : 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                                      }`}
                                    >
                                      {ev.type === 'trial' ? 'Clinical Trial' : 'Publication'}
                                    </span>
                                    <span className="text-xs font-mono font-medium text-gray-800">
                                      {ev.id}
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-600 line-clamp-1 group-hover:text-blue-600">
                                    {ev.title}
                                  </p>
                                </div>
                                <ExternalLink className="w-3.5 h-3.5 text-gray-400 group-hover:text-blue-500 shrink-0 mt-1" />
                              </a>
                            ))}
                          </div>
                        ) : (
                          <p className="text-xs text-gray-400 italic">
                            No direct clinical trial or publication records found indexed for this exact drug-condition pair.
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer attribution */}
      <div className="border-t pt-3 flex items-center justify-between text-[11px] text-gray-400">
        <span>Source: Open Targets Platform &amp; ChEMBL</span>
        <span>Curated ontology mapping</span>
      </div>
    </div>
  );
}
