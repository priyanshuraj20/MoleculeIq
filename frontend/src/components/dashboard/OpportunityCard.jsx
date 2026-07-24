import React from 'react';
import { HelpCircle, Info } from 'lucide-react';

/**
 * ScoreBar — read-only horizontal bar for a 0–100 score.
 */
function ScoreBar({ value }) {
  const pct = Math.min(100, Math.max(0, value ?? 0));
  return (
    <div className="w-full bg-slate-100 rounded-full h-1.5">
      <div className="bg-indigo-500 h-1.5 rounded-full transition-all" style={{ width: `${pct}%` }} />
    </div>
  );
}

/**
 * OpportunityCard
 * Feature 2 — Opportunity Score & Audit Explanation
 *
 * Props:
 *   score      OpportunityScore object from ResearchContext (or null)
 *   metadata   ResearchMetadata object from ResearchContext (or null)
 *   isLoading  boolean
 */
export default function OpportunityCard({ score, metadata, isLoading }) {
  const subScores = score
    ? [
        {
          label: 'Clinical Evidence',
          value: score.clinical_score,
          explanation: metadata?.total_trials > 0
            ? `${metadata.total_trials} trials identified (${metadata.active_trials_count ?? 0} active, ${metadata.completed_trials_count ?? 0} completed).`
            : 'Limited clinical trial evidence available.',
        },
        {
          label: 'Scientific Literature',
          value: score.research_score,
          explanation: metadata?.total_publications > 0
            ? `${metadata.total_publications.toLocaleString()} publications indexed (${metadata.highly_cited_papers_count ?? 0} highly cited).`
            : 'Sparse scientific publication footprint.',
        },
        {
          label: 'Market Intelligence',
          value: score.market_score,
          explanation: metadata?.global_market_size_usd_mn != null
            ? `Global market size estimated at $${(metadata.global_market_size_usd_mn >= 1000 ? (metadata.global_market_size_usd_mn / 1000).toFixed(1) + 'B' : metadata.global_market_size_usd_mn + 'M')} with ${metadata.latest_market_cagr ?? 0}% CAGR.`
            : 'Market sales data unavailable.',
        },
        {
          label: 'Patent Landscape',
          value: score.patent_score,
          explanation: metadata?.fto_summary && metadata.fto_summary !== 'No patent data available'
            ? metadata.fto_summary
            : `${metadata?.patent_count ?? 0} patent records analyzed.`,
        },
      ]
    : null;

  // Extract explicit backend score breakdown explanations if present
  const backendExplanations = score?.score_breakdown?.explanation ?? [];

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-5">
      {/* Header */}
      <div className="space-y-0.5">
        <h2 className="text-base font-semibold text-slate-900">Opportunity Score</h2>
        <p className="text-xs text-slate-500">
          Deterministic commercial viability score synthesized across research domains.
        </p>
      </div>

      {/* Primary score */}
      {isLoading ? (
        <div className="space-y-2">
          <div className="h-10 w-32 bg-slate-100 rounded animate-pulse" />
          <div className="h-4 w-48 bg-slate-100 rounded animate-pulse" />
        </div>
      ) : score ? (
        <div className="flex items-end gap-6">
          <div>
            <p className="text-4xl font-bold text-slate-900 tracking-tight">
              {score.overall_score.toFixed(1)}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">Overall Score / 100</p>
          </div>
          <div className="pb-1">
            <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-semibold">
              {score.confidence_score.toFixed(0)}% Confidence
            </span>
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-400">Run a search to compute the opportunity score.</p>
      )}

      <div className="border-t border-slate-100" />

      {/* Sub-scores & Why Explanations (Feature 2) */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="space-y-1.5">
              <div className="h-3 w-40 bg-slate-100 rounded animate-pulse" />
              <div className="h-1.5 w-full bg-slate-100 rounded-full animate-pulse" />
            </div>
          ))}
        </div>
      ) : subScores ? (
        <div className="space-y-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
            Domain Score Breakdown & Rationale
          </p>
          {subScores.map(({ label, value, explanation }) => (
            <div key={label} className="space-y-1 bg-slate-50/70 p-3 rounded-lg border border-slate-100">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-900 font-semibold">{label}</span>
                <span className="text-indigo-600 font-bold tabular-nums">{value?.toFixed(1) ?? '—'}</span>
              </div>
              <ScoreBar value={value} />
              <p className="text-[11px] text-slate-500 pt-1 leading-normal flex items-start gap-1">
                <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                <span>{explanation}</span>
              </p>
            </div>
          ))}

          {/* Backend explicit audit logs if present */}
          {backendExplanations.length > 0 && (
            <div className="pt-2 border-t border-slate-100 space-y-1">
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide flex items-center gap-1">
                <HelpCircle className="w-3 h-3 text-slate-400" />
                Scoring Heuristic Audit Log
              </p>
              <ul className="list-disc list-inside text-[11px] text-slate-500 space-y-0.5 pl-1">
                {backendExplanations.map((exp, i) => (
                  <li key={i}>{exp}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Domain Breakdown</p>
          {['Clinical Evidence', 'Scientific Literature', 'Market Intelligence', 'Patent Landscape'].map((label) => (
            <div key={label} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">{label}</span>
                <span className="text-slate-300">—</span>
              </div>
              <ScoreBar value={0} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
