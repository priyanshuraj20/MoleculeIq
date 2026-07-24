import React from 'react';
import {
  User,
  LayoutDashboard,
  Server,
  Network,
  Cpu,
  TrendingUp,
  Globe,
  Activity,
  ShieldCheck,
  BookOpen,
  FileText,
  Database,
  Cloud,
  HardDrive,
  Library,
  Download,
  ArrowDown,
} from 'lucide-react';

/**
 * System Architecture Flow Tree Diagram.
 * Rendered in Light Mode SaaS Aesthetic matching MoleculeIQ design tokens.
 *
 * Flow:
 *   User -> React Vite Frontend -> FastAPI Backend -> LangGraph Orchestrator -> Master Agent
 *     |-> Specialized Agents -> Connected Data Sources & Output Engines
 */

const MAIN_PIPELINE = [
  { label: 'User', icon: User, badge: 'CLIENT', color: 'text-slate-900 border-indigo-200 bg-indigo-50/70' },
  { label: 'React Vite Frontend', icon: LayoutDashboard, badge: 'UI LAYER', color: 'text-slate-900 border-slate-200 bg-slate-50' },
  { label: 'FastAPI Backend', icon: Server, badge: 'GATEWAY', color: 'text-slate-900 border-slate-200 bg-slate-50' },
  { label: 'LangGraph Orchestrator', icon: Network, badge: 'STATE MACHINE', color: 'text-slate-900 border-indigo-200 bg-indigo-50/70' },
  { label: 'Master Agent', icon: Cpu, badge: 'COORDINATOR', color: 'text-slate-900 border-slate-200 bg-slate-50' },
];

const PARALLEL_BRANCHES = [
  {
    agent: 'Market Sales Agent',
    agentIcon: TrendingUp,
    target: 'Supabase (market_sales via SQL)',
    targetIcon: Database,
  },
  {
    agent: 'EXIM Trade Agent',
    agentIcon: Globe,
    target: 'UN Comtrade API (trade flows)',
    targetIcon: Cloud,
  },
  {
    agent: 'Clinical Trials Agent',
    agentIcon: Activity,
    target: 'ClinicalTrials.gov API v2',
    targetIcon: HardDrive,
  },
  {
    agent: 'Patent Landscape Agent',
    agentIcon: ShieldCheck,
    target: 'Supabase (patents & FTO)',
    targetIcon: Database,
  },
  {
    agent: 'Scientific Literature Agent',
    agentIcon: BookOpen,
    target: 'Europe PMC REST API',
    targetIcon: Library,
  },
  {
    agent: 'Report Generation Agent',
    agentIcon: FileText,
    target: 'Local PDF Generator (ReportLab)',
    targetIcon: Download,
  },
];

export default function ArchitectureDiagram() {
  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm text-slate-900 overflow-x-auto space-y-6">

      {/* Diagram Title Bar */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-indigo-600 animate-pulse" />
          <span className="text-xs font-mono font-bold tracking-wider text-slate-700 uppercase">
            System Architecture DAG Flow
          </span>
        </div>
        <span className="text-[11px] font-mono text-indigo-700 bg-indigo-50 border border-indigo-100 px-2.5 py-1 rounded-md font-semibold">
          FastAPI + LangGraph Orchestration
        </span>
      </div>

      {/* Main Vertical Spine (User -> Master Agent) */}
      <div className="flex flex-col items-center space-y-2">
        {MAIN_PIPELINE.map((step, idx) => {
          const Icon = step.icon;

          return (
            <React.Fragment key={step.label}>
              {/* Card Node */}
              <div className={`w-64 sm:w-72 rounded-xl p-3 border shadow-xs flex items-center justify-between gap-3 ${step.color}`}>
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="p-1.5 rounded-lg bg-white border border-slate-200 text-indigo-600 shrink-0 shadow-xs">
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-xs font-bold font-mono tracking-tight text-slate-900 truncate">
                    {step.label}
                  </span>
                </div>
                <span className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600 shrink-0">
                  {step.badge}
                </span>
              </div>

              {/* Vertical Connecting Stem */}
              <div className="flex flex-col items-center text-indigo-500">
                <div className="w-px h-3 bg-indigo-200" />
                <ArrowDown className="w-3.5 h-3.5 text-indigo-600 -my-0.5" />
                <div className="w-px h-3 bg-indigo-200" />
              </div>
            </React.Fragment>
          );
        })}
      </div>

      {/* Horizontal Branching Tree (Master Agent -> Parallel Agents & Data Sources) */}
      <div className="pt-2 space-y-4">

        {/* Tree Branch Header Line (Desktop) */}
        <div className="hidden lg:block relative">
          <div className="absolute top-0 left-[8%] right-[8%] h-px bg-indigo-200" />
        </div>

        {/* Parallel Agent Columns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
          {PARALLEL_BRANCHES.map((b) => {
            const AgentIcon  = b.agentIcon;
            const TargetIcon = b.targetIcon;

            return (
              <div key={b.agent} className="flex flex-col items-center space-y-2 group">
                
                {/* Agent Card */}
                <div className="w-full bg-white border border-slate-200 group-hover:border-indigo-400 rounded-xl p-3 flex flex-col items-center text-center space-y-1.5 transition-colors shadow-xs">
                  <div className="p-1.5 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600">
                    <AgentIcon className="w-4 h-4" />
                  </div>
                  <span className="text-[11px] font-bold font-mono text-slate-900 leading-tight">
                    {b.agent}
                  </span>
                </div>

                {/* Connecting Arrow down to target source */}
                <div className="flex flex-col items-center text-indigo-500">
                  <div className="w-px h-2 bg-indigo-200" />
                  <ArrowDown className="w-3 h-3 text-indigo-600 -my-0.5" />
                </div>

                {/* Target Data Source / Output Card */}
                <div className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 flex flex-col items-center text-center space-y-1.5 shadow-xs">
                  <div className="p-1.5 rounded-lg bg-white border border-slate-200 text-slate-500">
                    <TargetIcon className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-[10px] font-mono text-slate-600 leading-tight">
                    {b.target}
                  </span>
                </div>

              </div>
            );
          })}
        </div>

      </div>

    </div>
  );
}
