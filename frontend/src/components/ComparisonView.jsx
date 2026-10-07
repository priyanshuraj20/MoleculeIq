import React from 'react';
import { Award, CheckCircle2, ArrowRight, ShieldCheck, TrendingUp, Activity, RotateCcw } from 'lucide-react';

export default function ComparisonView({ comparisonData, onReset }) {
  if (!comparisonData) return null;

  const {
    molecule_a_name,
    molecule_b_name,
    molecule_a_context,
    molecule_b_context,
    clinical_comparison,
    literature_comparison,
    patent_comparison,
    market_comparison,
    overall_winner,
    score_difference,
    executive_summary,
  } = comparisonData;

  const scoreA = (molecule_a_context?.score?.overall_score != null && !isNaN(molecule_a_context.score.overall_score))
    ? Number(molecule_a_context.score.overall_score)
    : 0;
  const scoreB = (molecule_b_context?.score?.overall_score != null && !isNaN(molecule_b_context.score.overall_score))
    ? Number(molecule_b_context.score.overall_score)
    : 0;

  const winnerName =
    overall_winner === 'molecule_a'
      ? (molecule_a_name || 'Compound A')
      : overall_winner === 'molecule_b'
      ? (molecule_b_name || 'Compound B')
      : 'Equal Rating';

  const comparisons = [
    clinical_comparison,
    literature_comparison,
    patent_comparison,
    market_comparison,
  ].filter(Boolean);

  return (
    <div className="w-full space-y-6">
      {/* Top Banner - Light Corporate Theme */}
      <div 
        className="bg-white rounded-xl p-6 border space-y-4"
        style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
      >
        <div 
          className="flex items-center justify-between border-b pb-4 flex-wrap gap-3"
          style={{ borderColor: 'var(--color-border-light)' }}
        >
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-blue-700">
                Head-to-Head Comparative Benchmark
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                Dual LangGraph Pipeline
              </span>
            </div>
            <h2 className="text-xl font-bold mt-1 text-gray-900">
              {molecule_a_name || 'Molecule A'} <span className="text-gray-400 font-normal">vs</span> {molecule_b_name || 'Molecule B'}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <span className="text-xs text-gray-500 font-medium">Preferred Candidate</span>
              <div className="flex items-center gap-1.5 text-teal-700 font-bold text-base mt-0.5">
                <Award className="w-4 h-4 text-teal-600" />
                {winnerName}
                {overall_winner !== 'tie' && score_difference != null && (
                  <span className="text-xs text-teal-800 font-medium ml-1">
                    (+{score_difference} pts)
                  </span>
                )}
              </div>
            </div>
            {onReset && (
              <button
                type="button"
                onClick={onReset}
                className="px-3 py-1.5 text-xs font-medium border rounded-lg bg-gray-50 hover:bg-gray-100 text-gray-700 flex items-center gap-1.5 transition-colors cursor-pointer"
                style={{ borderColor: 'var(--color-border)' }}
                title="Start a new search"
              >
                <RotateCcw className="w-3.5 h-3.5 text-gray-500" />
                New Search
              </button>
            )}
          </div>
        </div>

        {/* Score Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div 
            className={`p-4 rounded-lg border ${
              overall_winner === 'molecule_a'
                ? 'bg-blue-50/40 border-blue-300'
                : 'bg-gray-50/50 border-gray-200'
            }`}
          >
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold text-base text-gray-900">{molecule_a_name || 'Molecule A'}</h3>
              {overall_winner === 'molecule_a' && (
                <span className="px-2 py-0.5 text-xs bg-teal-50 text-teal-700 border border-teal-200 rounded font-medium">
                  Highest Overall
                </span>
              )}
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {Number(scoreA).toFixed(1)} <span className="text-xs font-normal text-gray-500">/ 100</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Data Confidence: {molecule_a_context?.score?.confidence_score != null ? `${Number(molecule_a_context.score.confidence_score).toFixed(0)}%` : 'N/A'}
            </p>
          </div>

          <div 
            className={`p-4 rounded-lg border ${
              overall_winner === 'molecule_b'
                ? 'bg-blue-50/40 border-blue-300'
                : 'bg-gray-50/50 border-gray-200'
            }`}
          >
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold text-base text-gray-900">{molecule_b_name || 'Molecule B'}</h3>
              {overall_winner === 'molecule_b' && (
                <span className="px-2 py-0.5 text-xs bg-teal-50 text-teal-700 border border-teal-200 rounded font-medium">
                  Highest Overall
                </span>
              )}
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {Number(scoreB).toFixed(1)} <span className="text-xs font-normal text-gray-500">/ 100</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Data Confidence: {molecule_b_context?.score?.confidence_score != null ? `${Number(molecule_b_context.score.confidence_score).toFixed(0)}%` : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Domain Comparison Table */}
      <div 
        className="bg-white rounded-xl p-6 border space-y-4"
        style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
      >
        <h3 
          className="text-sm font-bold uppercase tracking-wider text-gray-600 border-b pb-3"
          style={{ borderColor: 'var(--color-border-light)' }}
        >
          Domain Breakdown &amp; Differential Advantage
        </h3>

        <div className="divide-y divide-gray-100">
          {comparisons.map((item, idx) => (
            <div key={idx} className="py-4 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-gray-900">{item.domain_name || `Domain ${idx + 1}`}</span>
                <span className="text-xs font-medium px-2 py-0.5 bg-gray-100 text-gray-700 rounded border border-gray-200">
                  Advantage: {item.winner === 'molecule_a' ? (molecule_a_name || 'Compound A') : item.winner === 'molecule_b' ? (molecule_b_name || 'Compound B') : 'Parity'}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div 
                  className={`p-3 rounded-lg border ${
                    item.winner === 'molecule_a'
                      ? 'bg-teal-50/40 border-teal-200 text-gray-900'
                      : 'bg-gray-50 border-gray-200 text-gray-800'
                  }`}
                >
                  <span className="text-xs text-gray-500 font-medium block">{molecule_a_name || 'Molecule A'}</span>
                  <span className="font-semibold text-gray-900">{typeof item.molecule_a_val === 'object' ? JSON.stringify(item.molecule_a_val) : String(item.molecule_a_val ?? 'N/A')}</span>
                </div>
                <div 
                  className={`p-3 rounded-lg border ${
                    item.winner === 'molecule_b'
                      ? 'bg-teal-50/40 border-teal-200 text-gray-900'
                      : 'bg-gray-50 border-gray-200 text-gray-800'
                  }`}
                >
                  <span className="text-xs text-gray-500 font-medium block">{molecule_b_name || 'Molecule B'}</span>
                  <span className="font-semibold text-gray-900">{typeof item.molecule_b_val === 'object' ? JSON.stringify(item.molecule_b_val) : String(item.molecule_b_val ?? 'N/A')}</span>
                </div>
              </div>

              <p className="text-xs text-gray-600 mt-1">{typeof item.summary === 'object' ? JSON.stringify(item.summary) : String(item.summary ?? '')}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Strategic Executive Recommendation */}
      {executive_summary && (
        <div 
          className="bg-white rounded-xl p-6 border space-y-3"
          style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
        >
          <div className="flex items-center gap-2 text-gray-900 font-semibold text-sm">
            <TrendingUp className="w-4 h-4 text-blue-700" />
            Executive Synthesis &amp; Strategic Recommendation
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">
            {typeof executive_summary.strategic_recommendation === 'object'
              ? JSON.stringify(executive_summary.strategic_recommendation)
              : String(executive_summary.strategic_recommendation ?? '')}
          </p>

          {Array.isArray(executive_summary.key_differentiators) && executive_summary.key_differentiators.length > 0 && (
            <div 
              className="mt-4 pt-3 border-t space-y-2"
              style={{ borderColor: 'var(--color-border-light)' }}
            >
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block">
                Key Strategic Differentiators
              </span>
              <ul className="space-y-1.5">
                {executive_summary.key_differentiators.map((diff, i) => (
                  <li key={i} className="text-xs text-gray-700 flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                    <span>{typeof diff === 'object' ? JSON.stringify(diff) : String(diff)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
