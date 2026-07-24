import React from 'react';

/**
 * ReportSectionCard
 * Renders an independent executive report section with title, icon, divider,
 * and readable paragraphs adhering to 60–75 char max width.
 *
 * Props:
 *   id          string — element anchor ID (e.g. "clinical")
 *   title       string — section title
 *   icon        Lucide icon component
 *   content     string | array — section text content
 *   isHighlighted boolean — subtle border accent for Final Recommendation
 */
export default function ReportSectionCard({ id, title, icon: Icon, content, isHighlighted }) {
  // Format string content into readable paragraphs split on newlines
  const paragraphs = typeof content === 'string'
    ? content.split('\n\n').filter(Boolean)
    : Array.isArray(content)
    ? content
    : [String(content ?? '')];

  return (
    <section
      id={id}
      className={`bg-white rounded-xl p-6 sm:p-8 space-y-4 scroll-mt-36 border shadow-sm transition-all ${
        isHighlighted
          ? 'border-indigo-300 ring-1 ring-indigo-200 bg-gradient-to-b from-indigo-50/30 to-white'
          : 'border-slate-200'
      }`}
    >
      {/* Title & Icon Header */}
      <div className="flex items-center gap-3">
        {Icon && (
          <div
            className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
              isHighlighted
                ? 'bg-indigo-600 text-white'
                : 'bg-indigo-50 border border-indigo-100 text-indigo-600'
            }`}
          >
            <Icon className="w-4.5 h-4.5" />
          </div>
        )}
        <h2 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight">
          {title}
        </h2>
      </div>

      {/* Divider */}
      <div className="border-t border-slate-100" />

      {/* Paragraphs with max-w-prose for 60-75 char optimal reading width */}
      <div className="space-y-4 max-w-prose">
        {paragraphs.map((para, idx) => (
          <p
            key={idx}
            className="text-sm sm:text-base text-slate-700 leading-relaxed font-sans"
          >
            {para.trim()}
          </p>
        ))}
      </div>
    </section>
  );
}
