import React from 'react';
import { Award, CheckCircle2, ArrowRight, ShieldCheck, Zap } from 'lucide-react';

export default function ComparisonView({ comparisonData }) {
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

  const scoreA = molecule_a_context?.score?.overall_score ?? 0;
  const scoreB = molecule_b_context?.score?.overall_score ?? 0;

  const winnerName =
    overall_winner === 'molecule_a'
      ? molecule_a_name
      : overall_winner === 'molecule_b'
      ? molecule_b_name
      : 'Equal Rating';

  const comparisons = [
    clinical_comparison,
    literature_comparison,
    patent_comparison,
    market_comparison,
  ].filter(Boolean);

  return (
    <div className="w-full max-w-5xl mx-auto my-8 space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-xl border border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
              Comparative Analysis Mode
            </span>
            <h2 className="text-2xl font-bold mt-1 text-white">
              {molecule_a_name} <span className="text-indigo-400 font-normal">vs</span> {molecule_b_name}
            </h2>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400">Preferred Candidate</span>
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-lg mt-0.5">
              <Award className="w-5 h-5 text-emerald-400" />
              {winnerName}
              {overall_winner !== 'tie' && (
                <span className="text-xs text-emerald-300 font-normal ml-1">
                  (+{score_difference} pts)
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Score Cards Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className={`p-4 rounded-xl border ${overall_winner === 'molecule_a' ? 'bg-indigo-950/40 border-indigo-500/50' : 'bg-slate-800/50 border-slate-700'}`}>
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold text-lg text-white">{molecule_a_name}</h3>
              {overall_winner === 'molecule_a' && (
                <span className="px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full font-medium">
                  Highest Score
                </span>
              )}
            </div>
            <div className="text-3xl font-extrabold text-white">
              {scoreA.toFixed(1)} <span className="text-sm font-normal text-slate-400">/ 100</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Confidence: {molecule_a_context?.score?.confidence_score?.toFixed(0)}%
            </p>
          </div>

          <div className={`p-4 rounded-xl border ${overall_winner === 'molecule_b' ? 'bg-indigo-950/40 border-indigo-500/50' : 'bg-slate-800/50 border-slate-700'}`}>
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold text-lg text-white">{molecule_b_name}</h3>
              {overall_winner === 'molecule_b' && (
                <span className="px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full font-medium">
                  Highest Score
                </span>
              )}
            </div>
            <div className="text-3xl font-extrabold text-white">
              {scoreB.toFixed(1)} <span className="text-sm font-normal text-slate-400">/ 100</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Confidence: {molecule_b_context?.score?.confidence_score?.toFixed(0)}%
            </p>
          </div>
        </div>
      </div>

      {/* Domain Comparison Table */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-lg font-bold text-slate-900 border-b pb-3 border-slate-100">
          Domain Breakdown Comparison
        </h3>

        <div className="divide-y divide-slate-100">
          {comparisons.map((item, idx) => (
            <div key={idx} className="py-4 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-bold text-slate-800">{item.domain_name}</span>
                <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md">
                  Advantage: {item.winner === 'molecule_a' ? molecule_a_name : item.winner === 'molecule_b' ? molecule_b_name : 'Equal'}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className={`p-3 rounded-lg border text-slate-800 ${item.winner === 'molecule_a' ? 'bg-emerald-50/50 border-emerald-200' : 'bg-slate-50 border-slate-100'}`}>
                  <span className="text-xs text-slate-500 font-semibold block">{molecule_a_name}</span>
                  <span className="font-medium text-slate-900">{item.molecule_a_val}</span>
                </div>
                <div className={`p-3 rounded-lg border text-slate-800 ${item.winner === 'molecule_b' ? 'bg-emerald-50/50 border-emerald-200' : 'bg-slate-50 border-slate-100'}`}>
                  <span className="text-xs text-slate-500 font-semibold block">{molecule_b_name}</span>
                  <span className="font-medium text-slate-900">{item.molecule_b_val}</span>
                </div>
              </div>

              <p className="text-xs text-slate-600 italic mt-1">{item.summary}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Strategic Executive Recommendation */}
      {executive_summary && (
        <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 text-indigo-900 font-bold mb-2">
            <Zap className="w-5 h-5 text-indigo-600" />
            Executive Comparison Recommendation
          </div>
          <p className="text-sm text-indigo-950 leading-relaxed">
            {executive_summary.strategic_recommendation}
          </p>

          {executive_summary.key_differentiators?.length > 0 && (
            <div className="mt-4 pt-3 border-t border-indigo-100/80">
              <span className="text-xs font-bold text-indigo-800 uppercase tracking-wider block mb-2">
                Key Strategic Differentiators
              </span>
              <ul className="space-y-1">
                {executive_summary.key_differentiators.map((diff, i) => (
                  <li key={i} className="text-xs text-indigo-900 flex items-start gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                    <span>{diff}</span>
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
