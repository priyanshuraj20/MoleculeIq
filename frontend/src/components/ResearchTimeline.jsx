import React from 'react';
import { Calendar, CheckCircle2, Clock, ShieldAlert } from 'lucide-react';

export default function ResearchTimeline({ context }) {
  if (!context) return null;

  const trials = context.clinical?.trials || [];
  const pubs = context.literature?.publications || [];
  const patents = context.patent?.patents || [];

  const timelineEvents = [];

  trials.forEach((t) => {
    if (t.completion_date) {
      timelineEvents.push({
        year: t.completion_date.substring(0, 4),
        date: t.completion_date,
        type: 'Clinical Trial',
        title: t.title || t.nct_id,
        badge: t.overall_status,
        color: 'bg-emerald-500',
      });
    }
  });

  pubs.forEach((p) => {
    if (p.publication_year) {
      timelineEvents.push({
        year: String(p.publication_year),
        date: String(p.publication_year),
        type: 'Publication',
        title: p.title,
        badge: `${p.citation_count || 0} citations`,
        color: 'bg-blue-500',
      });
    }
  });

  patents.forEach((p) => {
    if (p.expiry_date) {
      timelineEvents.push({
        year: p.expiry_date.substring(0, 4),
        date: p.expiry_date,
        type: 'Patent Expiry',
        title: `Patent ${p.patent_number} Expiration Horizon`,
        badge: p.status,
        color: 'bg-purple-500',
      });
    }
  });

  // Sort timeline events chronologically
  timelineEvents.sort((a, b) => (b.year || '').localeCompare(a.year || ''));

  const sortedEvents = timelineEvents.slice(0, 6);

  if (sortedEvents.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4 my-6">
      <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
        <Calendar className="w-5 h-5 text-indigo-600" />
        <h3 className="text-base font-bold text-slate-900">Research Milestone Timeline</h3>
      </div>

      <div className="relative border-l-2 border-slate-100 ml-4 space-y-6 py-2">
        {sortedEvents.map((evt, idx) => (
          <div key={idx} className="relative pl-6">
            <span className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-white ${evt.color} shadow-sm`} />

            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">{evt.date} • {evt.type}</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">{evt.badge}</span>
            </div>

            <p className="text-sm font-semibold text-slate-900 mt-1 line-clamp-1">{evt.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
