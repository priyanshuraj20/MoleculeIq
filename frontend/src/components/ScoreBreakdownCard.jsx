import React from 'react';
import { Target, TrendingUp, Activity, ShieldCheck, BookOpen } from 'lucide-react';

export default function ScoreBreakdownCard({ scoreObj }) {
  if (!scoreObj) return null;

  const { overall_score, market_score, clinical_score, patent_score, research_score, category_weights } = scoreObj;
  const weights = category_weights || { market: 30, clinical: 25, patent: 25, literature: 20 };

  const categories = [
    { label: 'Market Opportunity', score: market_score, weight: weights.market, color: 'bg-emerald-500', icon: TrendingUp },
    { label: 'Clinical Evidence', score: clinical_score, weight: weights.clinical, color: 'bg-blue-500', icon: Activity },
    { label: 'Patent & FTO Landscape', score: patent_score, weight: weights.patent, color: 'bg-purple-500', icon: ShieldCheck },
    { label: 'Scientific Literature', score: research_score, weight: weights.literature, color: 'bg-amber-500', icon: BookOpen },
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4 my-6">
      <div className="flex justify-between items-center border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-indigo-600" />
          <h3 className="text-base font-bold text-slate-900">Commercial Opportunity Score Explanation</h3>
        </div>
        <div className="text-right">
          <span className="text-2xl font-black text-slate-900">{overall_score?.toFixed(1)}</span>
          <span className="text-xs text-slate-400 font-normal"> / 100</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map((c, idx) => {
          const Icon = c.icon;
          const weightedContribution = ((c.score || 0) * (c.weight / 100)).toFixed(1);

          return (
            <div key={idx} className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4 text-slate-600" />
                  <span className="text-xs font-bold text-slate-800">{c.label}</span>
                </div>
                <span className="text-xs font-semibold text-slate-500">Weight: {c.weight}%</span>
              </div>

              <div className="flex items-baseline justify-between">
                <span className="text-lg font-extrabold text-slate-900">{c.score?.toFixed(0) ?? 0} <span className="text-xs font-normal text-slate-500">/ 100</span></span>
                <span className="text-xs font-bold text-indigo-600">+{weightedContribution} pts</span>
              </div>

              <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                <div className={`h-full ${c.color}`} style={{ width: `${Math.min(100, c.score || 0)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
