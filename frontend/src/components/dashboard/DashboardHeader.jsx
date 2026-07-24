import React from 'react';
import { FlaskConical } from 'lucide-react';

/**
 * DashboardHeader
 * Displays the page title and a one-line description.
 * molecule: optional string — the currently analyzed molecule name.
 */
export default function DashboardHeader({ molecule }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
      <div className="space-y-0.5">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Research Dashboard
        </h1>
        <p className="text-slate-500 text-sm">
          Analyze pharmaceutical research intelligence for any molecule.
        </p>
      </div>

      {molecule && (
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-700 text-sm font-medium shrink-0">
          <FlaskConical className="w-4 h-4" />
          {molecule}
        </div>
      )}
    </div>
  );
}
