import React from 'react';
import { Calendar } from 'lucide-react';

export default function ResearchTimeline({ context }) {
  if (!context) return null;

  const trials  = context.clinical?.trials || [];
  const pubs    = context.literature?.publications || [];
  const patents = context.patent?.patents || [];

  const timelineEvents = [];

  trials.forEach((t) => {
    if (t.completion_date) {
      timelineEvents.push({
        year:  t.completion_date.substring(0, 4),
        date:  t.completion_date,
        type:  'Clinical Trial',
        title: t.title || t.nct_id,
        badge: t.overall_status,
        dotColor: 'var(--color-teal)',
      });
    }
  });

  pubs.forEach((p) => {
    if (p.publication_year) {
      timelineEvents.push({
        year:  String(p.publication_year),
        date:  String(p.publication_year),
        type:  'Publication',
        title: p.title,
        badge: `${p.citation_count || 0} citations`,
        dotColor: 'var(--color-blue)',
      });
    }
  });

  patents.forEach((p) => {
    if (p.expiry_date) {
      timelineEvents.push({
        year:  p.expiry_date.substring(0, 4),
        date:  p.expiry_date,
        type:  'Patent Expiry',
        title: `Patent ${p.patent_number} Expiration Horizon`,
        badge: p.status,
        dotColor: '#7c3aed',
      });
    }
  });

  timelineEvents.sort((a, b) => (b.year || '').localeCompare(a.year || ''));
  const sortedEvents = timelineEvents.slice(0, 6);

  if (sortedEvents.length === 0) return null;

  return (
    <div
      className="bg-white border rounded-xl p-6 space-y-4"
      style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)' }}
    >
      {/* Header */}
      <div
        className="flex items-center gap-2 border-b pb-3"
        style={{ borderColor: 'var(--color-border-light)' }}
      >
        <Calendar className="w-5 h-5" style={{ color: 'var(--color-blue)' }} />
        <h3 className="text-base font-semibold" style={{ color: 'var(--color-text)' }}>
          Research Milestone Timeline
        </h3>
      </div>

      {/* Timeline */}
      <div
        className="relative border-l-2 ml-4 space-y-6 py-2"
        style={{ borderColor: 'var(--color-border-light)' }}
      >
        {sortedEvents.map((evt, idx) => (
          <div key={idx} className="relative pl-6">
            <span
              className="absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-white shadow-sm"
              style={{ backgroundColor: evt.dotColor }}
            />

            <div className="flex items-center justify-between">
              <span
                className="text-xs font-bold uppercase tracking-wider"
                style={{ color: 'var(--color-text-faint)' }}
              >
                {evt.date} · {evt.type}
              </span>
              <span
                className="text-xs font-semibold px-2 py-0.5 rounded border"
                style={{
                  backgroundColor: 'var(--color-bg)',
                  borderColor: 'var(--color-border-light)',
                  color: 'var(--color-text-muted)',
                }}
              >
                {evt.badge}
              </span>
            </div>

            <p
              className="text-sm font-semibold mt-1 line-clamp-1"
              style={{ color: 'var(--color-text)' }}
            >
              {evt.title}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
