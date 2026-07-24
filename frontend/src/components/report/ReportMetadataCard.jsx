import React from 'react';
import { FlaskConical, Award, ShieldCheck, Calendar, CheckCircle2 } from 'lucide-react';

/**
 * ReportMetadataCard
 * Displays 5 compact metadata cards:
 * Molecule Name, Opportunity Score, Confidence, Generated Date, Research Status.
 *
 * Props:
 *   moleculeName     string
 *   overallScore     number | string
 *   confidenceScore  number | string
 *   generatedDate    string
 *   status           string
 */
export default function ReportMetadataCard({
  moleculeName,
  overallScore,
  confidenceScore,
  generatedDate,
  status = 'Completed',
}) {
  const items = [
    {
      icon: FlaskConical,
      label: 'Target Molecule',
      value: moleculeName || '—',
      accent: 'text-indigo-600',
    },
    {
      icon: Award,
      label: 'Opportunity Score',
      value: typeof overallScore === 'number' ? `${overallScore.toFixed(1)} / 100` : (overallScore || '—'),
      accent: 'text-slate-900',
    },
    {
      icon: ShieldCheck,
      label: 'Data Confidence',
      value: typeof confidenceScore === 'number' ? `${confidenceScore.toFixed(0)}%` : (confidenceScore || '100%'),
      accent: 'text-emerald-600',
    },
    {
      icon: Calendar,
      label: 'Generated Date',
      value: generatedDate ? new Date(generatedDate).toLocaleDateString() : new Date().toLocaleDateString(),
      accent: 'text-slate-700',
    },
    {
      icon: CheckCircle2,
      label: 'Research Status',
      value: status,
      accent: 'text-emerald-600',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      {items.map((item, i) => {
        const Icon = item.icon;
        return (
          <div
            key={i}
            className="bg-white rounded-xl border border-slate-200 p-3.5 space-y-1 shadow-sm"
          >
            <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
              <Icon className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate">{item.label}</span>
            </div>
            <p className={`text-base sm:text-lg font-bold tracking-tight ${item.accent} truncate`}>
              {item.value}
            </p>
          </div>
        );
      })}
    </div>
  );
}
