import React from 'react';
import { Search, Network, Cpu, Layers, FileText } from 'lucide-react';

const STEPS = [
  {
    step: 1,
    title: 'Search Molecule',
    desc: 'User enters a target pharmaceutical drug or chemical molecule name.',
    icon: Search,
  },
  {
    step: 2,
    title: 'Research Pipeline',
    desc: 'LangGraph orchestrator initializes DAG state and dispatches worker agents.',
    icon: Network,
  },
  {
    step: 3,
    title: 'Parallel Analysis',
    desc: 'Clinical, literature, patent, and market research nodes execute asynchronously.',
    icon: Cpu,
  },
  {
    step: 4,
    title: 'AI Synthesis',
    desc: 'Findings are aggregated into ResearchContext & scored via weighted heuristics.',
    icon: Layers,
  },
  {
    step: 5,
    title: 'Executive Report',
    desc: 'Generates McKinsey-style C-suite report with ReportLab PDF export.',
    icon: FileText,
  },
];

export default function ProcessSteps() {
  return (
    <div className="space-y-4">
      <div className="text-center max-w-lg mx-auto space-y-1">
        <h3 className="text-lg font-bold text-slate-900 tracking-tight">
          Execution Lifecycle
        </h3>
        <p className="text-xs text-slate-500">
          5-stage deterministic workflow from query input to C-suite delivery.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {STEPS.map(({ step, title, desc, icon: Icon }) => (
          <div
            key={step}
            className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm space-y-2 relative group hover:border-indigo-300 transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="w-6 h-6 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 font-bold text-xs flex items-center justify-center font-mono">
                {step}
              </span>
              <Icon className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 transition-colors" />
            </div>

            <h4 className="text-xs font-bold text-slate-900 tracking-tight">{title}</h4>
            <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
