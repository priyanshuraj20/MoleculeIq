import React from 'react';
import { HelpCircle, Info, TrendingUp } from 'lucide-react';

function ScoreBar({ value }) {
  const pct = Math.min(100, Math.max(0, value ?? 0));
  return (
    <div className="w-full h-1.5" style={{ backgroundColor: 'var(--color-border-light)', borderRadius: '3px' }}>
      <div
        className="h-1.5 transition-all"
        style={{ width: `${pct}%`, backgroundColor: 'var(--color-blue)', borderRadius: '3px' }}
      />
    </div>
  );
}

export default function OpportunityCard({ score, metadata, isLoading }) {
  const subScores = score ? [
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
  ] : null;

  const backendExplanations = score?.score_breakdown?.explanation ?? [];

  return (
    <div
      className="bg-white border p-6 space-y-5"
      style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)', borderRadius: '10px' }}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-0.5">
          <h2 className="text-base font-semibold" style={{ color: 'var(--color-text)' }}>
            Opportunity Score
          </h2>
          <p className="text-xs" style={{ color: 'var(--color-text-faint)' }}>
            Deterministic commercial viability score across research domains.
          </p>
        </div>
        <div
          className="w-8 h-8 flex items-center justify-center border"
          style={{ backgroundColor: 'var(--color-bg)', borderColor: 'var(--color-border-light)', borderRadius: '6px' }}
        >
          <TrendingUp className="w-4 h-4" style={{ color: 'var(--color-blue)' }} />
        </div>
      </div>

      {/* Primary score */}
      {isLoading ? (
        <div className="space-y-2">
          <div className="h-10 w-32 bg-gray-100 animate-pulse" style={{ borderRadius: '4px' }} />
          <div className="h-4 w-48 bg-gray-100 animate-pulse" style={{ borderRadius: '4px' }} />
        </div>
      ) : score ? (
        <div className="space-y-1">
          <div className="flex items-end gap-5">
            <div>
              <p className="text-4xl font-semibold tracking-tight tabular-nums" style={{ color: 'var(--color-text)', letterSpacing: '-0.02em' }}>
                {score.overall_score.toFixed(1)}
              </p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-faint)' }}>Overall Score / 100</p>
            </div>
            <div className="pb-1">
              <span
                className="inline-flex items-center px-2.5 py-1 text-xs font-semibold border"
                style={{ backgroundColor: '#f0fdfb', borderColor: 'var(--color-teal-dim)', color: 'var(--color-teal)', borderRadius: '4px' }}
              >
                {score.confidence_score.toFixed(0)}% Confidence
              </span>
            </div>
          </div>
          <p className="text-[11px] pt-1" style={{ color: 'var(--color-text-faint)' }}>
            Calculated from Clinical, Literature, Patent and Market evidence.
          </p>
        </div>
      ) : (
        <p className="text-sm" style={{ color: 'var(--color-text-faint)' }}>
          Run a search to compute the opportunity score.
        </p>
      )}

      <div className="border-t" style={{ borderColor: 'var(--color-border-light)' }} />

      {/* Sub-scores */}
      {isLoading ? (
        <div className="space-y-3">
          {[1,2,3,4].map((i) => (
            <div key={i} className="space-y-1.5">
              <div className="h-3 w-40 bg-gray-100 animate-pulse" style={{ borderRadius: '4px' }} />
              <div className="h-1.5 w-full bg-gray-100 animate-pulse" style={{ borderRadius: '3px' }} />
            </div>
          ))}
        </div>
      ) : subScores ? (
        <div className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--color-text-faint)' }}>
            Domain Score Breakdown &amp; Rationale
          </p>
          {subScores.map(({ label, value, explanation }) => (
            <div
              key={label}
              className="space-y-1 p-3 border"
              style={{ backgroundColor: 'var(--color-bg)', borderColor: 'var(--color-border-light)', borderRadius: '6px' }}
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold" style={{ color: 'var(--color-text)' }}>{label}</span>
                <span className="font-bold tabular-nums" style={{ color: 'var(--color-blue)' }}>{value?.toFixed(1) ?? '—'}</span>
              </div>
              <ScoreBar value={value} />
              <p className="text-[11px] pt-1 leading-normal flex items-start gap-1" style={{ color: 'var(--color-text-faint)' }}>
                <Info className="w-3 h-3 shrink-0 mt-0.5" />
                <span>{explanation}</span>
              </p>
            </div>
          ))}
          {backendExplanations.length > 0 && (
            <div className="pt-2 border-t space-y-1" style={{ borderColor: 'var(--color-border-light)' }}>
              <p className="text-[11px] font-semibold uppercase tracking-wide flex items-center gap-1" style={{ color: 'var(--color-text-faint)' }}>
                <HelpCircle className="w-3 h-3" /> Scoring Audit Log
              </p>
              <ul className="list-disc list-inside text-[11px] space-y-0.5 pl-1" style={{ color: 'var(--color-text-faint)' }}>
                {backendExplanations.map((exp, i) => <li key={i}>{exp}</li>)}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--color-text-faint)' }}>Domain Breakdown</p>
          {['Clinical Evidence', 'Scientific Literature', 'Market Intelligence', 'Patent Landscape'].map((label) => (
            <div key={label} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span style={{ color: 'var(--color-text-faint)' }}>{label}</span>
                <span style={{ color: 'var(--color-border)' }}>—</span>
              </div>
              <ScoreBar value={0} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
