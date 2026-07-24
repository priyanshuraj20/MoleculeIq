import React from 'react';
import {
  FileText,
  Award,
  Activity,
  BookOpen,
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';

const SECTIONS = [
  { id: 'summary',       label: 'Executive Summary',       icon: FileText },
  { id: 'commercial',    label: 'Commercial Opportunity',  icon: Award },
  { id: 'clinical',      label: 'Clinical Landscape',      icon: Activity },
  { id: 'scientific',    label: 'Scientific Literature',   icon: BookOpen },
  { id: 'market',        label: 'Market Intelligence',     icon: TrendingUp },
  { id: 'patent',        label: 'Patent Landscape',        icon: ShieldCheck },
  { id: 'risks',         label: 'Risk Assessment',         icon: AlertTriangle },
  { id: 'recommendation',label: 'Final Recommendation',    icon: CheckCircle2 },
];

/**
 * ReportSidebar
 * Lightweight sticky table of contents for smooth section navigation.
 *
 * Props:
 *   activeSection  string (optional)
 */
export default function ReportSidebar() {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <nav className="bg-white rounded-xl border border-slate-200 p-4 space-y-2 sticky top-36 shadow-sm hidden lg:block">
      <p className="text-xs font-bold text-slate-400 uppercase tracking-wider px-2 pb-1 border-b border-slate-100">
        Table of Contents
      </p>
      <div className="space-y-0.5 pt-1">
        {SECTIONS.map((sec) => {
          const Icon = sec.icon;
          return (
            <button
              key={sec.id}
              type="button"
              onClick={() => scrollTo(sec.id)}
              className="w-full flex items-center gap-2.5 px-2.5 py-2 text-xs font-medium text-slate-600 hover:text-indigo-600 hover:bg-indigo-50/60 rounded-lg transition-colors text-left"
            >
              <Icon className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span className="truncate">{sec.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
