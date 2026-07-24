import React from 'react';
import { Target, TrendingUp, Activity, ShieldCheck, BookOpen } from 'lucide-react';

export default function ScoreBreakdownCard({ scoreObj }) {
  if (!scoreObj) return null;

  const { overall_score, market_score, clinical_score, patent_score, research_score, category_weights } = scoreObj;
  const weights = category_weights || { market: 30, clinical: 25, patent: 25, literature: 20 };

  const categories = [
    {
      label: 'Market Opportunity',
      score: market_score,
      weight: weights.market,
      barColor: 'var(--color-teal)',
      icon: TrendingUp,
    },
    {
      label: 'Clinical Evidence',
      score: clinical_score,
      weight: weights.clinical,
      barColor: 'var(--color-blue)',
      icon: Activity,
    },
    {
      label: 'Patent & FTO Landscape',
      score: patent_score,
      weight: weights.patent,
      barColor: '#7c3aed',
      icon: ShieldCheck,
    },
    {
      label: 'Scientific Literature',
      score: research_score,
      weight: weights.literature,
      barColor: '#d97706',
      icon: BookOpen,
    },
  ];

  return (
    <div
      className="bg-white border rounded-xl p-6 space-y-4"
      style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)' }}
    >
      {/* Header */}
      <div
        className="flex justify-between items-center border-b pb-3"
        style={{ borderColor: 'var(--color-border-light)' }}
      >
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5" style={{ color: 'var(--color-blue)' }} />
          <h3 className="text-base font-semibold" style={{ color: 'var(--color-text)' }}>
            Commercial Opportunity Score Explanation
          </h3>
        </div>
        <div className="text-right">
          <span
            className="text-2xl font-bold tabular-nums"
            style={{ color: 'var(--color-text)', letterSpacing: '-0.01em' }}
          >
            {overall_score?.toFixed(1)}
          </span>
          <span className="text-xs font-normal ml-1" style={{ color: 'var(--color-text-faint)' }}>
            / 100
          </span>
        </div>
      </div>

      {/* Category grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map((c, idx) => {
          const Icon = c.icon;
          const weightedContribution = ((c.score || 0) * (c.weight / 100)).toFixed(1);

          return (
            <div
              key={idx}
              className="p-4 rounded-xl border space-y-2"
              style={{ backgroundColor: 'var(--color-bg)', borderColor: 'var(--color-border-light)' }}
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4" style={{ color: 'var(--color-text-muted)' }} />
                  <span className="text-xs font-bold" style={{ color: 'var(--color-text)' }}>
                    {c.label}
                  </span>
                </div>
                <span className="text-xs font-semibold" style={{ color: 'var(--color-text-faint)' }}>
                  Weight: {c.weight}%
                </span>
              </div>

              <div className="flex items-baseline justify-between">
                <span className="text-lg font-bold tabular-nums" style={{ color: 'var(--color-text)' }}>
                  {c.score?.toFixed(0) ?? 0}{' '}
                  <span className="text-xs font-normal" style={{ color: 'var(--color-text-faint)' }}>
                    / 100
                  </span>
                </span>
                <span className="text-xs font-bold" style={{ color: 'var(--color-blue)' }}>
                  +{weightedContribution} pts
                </span>
              </div>

              <div
                className="w-full h-1.5 rounded-full overflow-hidden"
                style={{ backgroundColor: 'var(--color-border-light)' }}
              >
                <div
                  className="h-full rounded-full transition-all"
                  style={{ width: `${Math.min(100, c.score || 0)}%`, backgroundColor: c.barColor }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
