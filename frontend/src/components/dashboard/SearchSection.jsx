import React from 'react';
import { Loader2, Search, FlaskConical } from 'lucide-react';
import ResearchProgressPanel from './ResearchProgressPanel';

const EXAMPLES = ['Metformin', 'Ibuprofen', 'Pembrolizumab', 'Semaglutide'];

/**
 * SearchSection
 * Controlled molecule search bar wired to the research hook.
 * Displays structured ResearchProgressPanel while pipeline is executing.
 *
 * Props:
 *   query          string
 *   onQueryChange  (string) => void
 *   onSubmit       () => void
 *   isLoading      boolean
 *   statusMessage  string  — live SSE status message
 *   lastEvent      string  — raw SSE event name
 */
export default function SearchSection({
  query,
  onQueryChange,
  onSubmit,
  isLoading,
  statusMessage,
  lastEvent,
}) {
  const handleKey = (e) => {
    if (e.key === 'Enter' && !isLoading) onSubmit();
  };

  return (
    <div className="space-y-4">
      {/* Search Input Box */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-3 shadow-sm">
        <div className="flex gap-2">
          <div className="relative flex-grow">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <input
              id="molecule-search"
              type="text"
              value={query}
              onChange={(e) => onQueryChange(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Search a molecule…"
              disabled={isLoading}
              className="w-full pl-9 pr-4 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            />
          </div>
          <button
            id="search-submit"
            type="button"
            onClick={onSubmit}
            disabled={isLoading || !query.trim()}
            className="shrink-0 inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Researching…
              </>
            ) : (
              <>
                <FlaskConical className="w-4 h-4" />
                Run Research
              </>
            )}
          </button>
        </div>

        {/* Example chips — hidden while loading */}
        {!isLoading && (
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 font-medium">Try:</span>
            {EXAMPLES.map((mol) => (
              <button
                key={mol}
                type="button"
                onClick={() => onQueryChange(mol)}
                className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600 font-mono hover:bg-slate-200 transition-colors"
              >
                {mol}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Feature 1: Structured Research Progress Panel during Loading State */}
      {isLoading && (
        <ResearchProgressPanel lastEvent={lastEvent} statusMessage={statusMessage} />
      )}
    </div>
  );
}
