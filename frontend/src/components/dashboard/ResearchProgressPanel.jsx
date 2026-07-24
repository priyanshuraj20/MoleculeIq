import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

const PROGRESS_STEPS = [
  {
    id: 'clinical',
    label: 'Collecting Clinical Evidence',
    startEvents: ['clinical_started'],
    completeEvents: ['clinical_completed', 'literature_started', 'literature_completed', 'market_started', 'market_completed', 'patent_started', 'patent_completed', 'aggregation_completed', 'scoring_completed', 'research_completed'],
  },
  {
    id: 'literature',
    label: 'Searching Scientific Literature',
    startEvents: ['literature_started'],
    completeEvents: ['literature_completed', 'market_started', 'market_completed', 'patent_started', 'patent_completed', 'aggregation_completed', 'scoring_completed', 'research_completed'],
  },
  {
    id: 'market',
    label: 'Analyzing Market Intelligence',
    startEvents: ['market_started'],
    completeEvents: ['market_completed', 'patent_started', 'patent_completed', 'aggregation_completed', 'scoring_completed', 'research_completed'],
  },
  {
    id: 'patent',
    label: 'Reviewing Patent Landscape',
    startEvents: ['patent_started'],
    completeEvents: ['patent_completed', 'aggregation_completed', 'scoring_completed', 'research_completed'],
  },
  {
    id: 'scoring',
    label: 'Calculating Opportunity Score',
    startEvents: ['aggregation_completed', 'scoring_completed'],
    completeEvents: ['research_completed'],
  },
  {
    id: 'report',
    label: 'Preparing Executive Report',
    startEvents: ['research_completed'],
    completeEvents: ['research_completed'],
  },
];

/**
 * ResearchProgressPanel
 * Structured progress panel showing pipeline execution steps driven by SSE events.
 *
 * Props:
 *   lastEvent      string — raw SSE event name (e.g. 'clinical_started')
 *   statusMessage  string — live human-readable progress text
 */
export default function ResearchProgressPanel({ lastEvent, statusMessage }) {
  const getStepState = (step) => {
    if (step.completeEvents.includes(lastEvent)) {
      return 'completed';
    }
    if (step.startEvents.includes(lastEvent)) {
      return 'in_progress';
    }
    return 'pending';
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
          <h3 className="text-sm font-semibold text-slate-900">Research Pipeline Progress</h3>
        </div>
        <span className="text-xs text-indigo-600 font-medium">{statusMessage}</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {PROGRESS_STEPS.map((step) => {
          const state = getStepState(step);
          return (
            <div
              key={step.id}
              className={`flex items-center gap-2.5 p-2.5 rounded-lg border text-xs font-medium transition-colors ${
                state === 'completed'
                  ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                  : state === 'in_progress'
                  ? 'bg-indigo-50 border-indigo-200 text-indigo-900'
                  : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              {state === 'completed' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              ) : state === 'in_progress' ? (
                <Loader2 className="w-4 h-4 text-indigo-600 animate-spin shrink-0" />
              ) : (
                <Circle className="w-4 h-4 text-slate-300 shrink-0" />
              )}
              <span className="truncate">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
