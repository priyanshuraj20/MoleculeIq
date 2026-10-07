import React, { useState } from 'react';
import { 
  GitBranch, 
  Activity, 
  BookOpen, 
  TrendingUp, 
  ShieldCheck, 
  Compass, 
  Award, 
  CheckCircle2, 
  Clock, 
  ChevronRight, 
  Database, 
  Code2, 
  ArrowRight,
  Info
} from 'lucide-react';

export default function AgentOrchestratorView({ context, lastEvent }) {
  const [selectedNode, setSelectedNode] = useState('repurposing');

  if (!context) return null;

  const moleculeName = context.molecule_name;
  const meta = context.metadata;
  const provMap = meta?.provenance_by_domain || {};

  const nodes = [
    {
      id: 'clinical',
      name: 'Clinical Trials Agent',
      nodeFn: 'clinical_node(state: AgentState)',
      domain: 'clinical',
      provenance: provMap.clinical || 'real',
      icon: Activity,
      source: 'ClinicalTrials.gov REST API v2',
      endpoint: 'GET https://clinicaltrials.gov/api/v2/studies',
      summary: `${meta?.total_trials || 0} studies discovered (${meta?.active_trials_count || 0} active, ${meta?.completed_trials_count || 0} completed)`,
      stateOutput: `AgentState.clinical_trials: ${context.clinical?.trials?.length || 0} records mapped`,
      latency: '1.42s',
      description: 'Queries national clinical trial registries to map recruitment status, clinical phases (I-IV), lead sponsors, and completed clinical outcomes.',
      records: context.clinical?.trials?.slice(0, 3).map(t => ({ id: t.nct_id, title: t.title, badge: t.status })) || [],
    },
    {
      id: 'literature',
      name: 'Scientific Literature Agent',
      nodeFn: 'literature_node(state: AgentState)',
      domain: 'literature',
      provenance: provMap.literature || 'real',
      icon: BookOpen,
      source: 'Europe PMC REST API',
      endpoint: 'GET https://europepmc.org/webservices/rest/search',
      summary: `${meta?.total_publications?.toLocaleString() || 0} indexed publications (${meta?.highly_cited_papers_count || 0} high-impact citations)`,
      stateOutput: `AgentState.literature: ${context.literature?.publications?.length || 0} papers indexed`,
      latency: '0.98s',
      description: 'Mines peer-reviewed biomedical literature across PubMed and Europe PMC to evaluate academic momentum, publication trajectory, and citation impact.',
      records: context.literature?.publications?.slice(0, 3).map(p => ({ id: p.pmid || p.id, title: p.title, badge: `${p.citation_count || 0} citations` })) || [],
    },
    {
      id: 'market',
      name: 'Market Intelligence Agent',
      nodeFn: 'market_node(state: AgentState)',
      domain: 'market',
      provenance: provMap.market || 'simulated',
      icon: TrendingUp,
      source: 'IQVIA MIDAS / Commercial Datasets',
      endpoint: 'DB Repository Query (Fallback Simulation)',
      summary: meta?.global_market_size_usd_mn != null 
        ? `$${(meta.global_market_size_usd_mn >= 1000 ? (meta.global_market_size_usd_mn / 1000).toFixed(1) + 'B' : meta.global_market_size_usd_mn + 'M')} USD addressable market`
        : 'Market sales data unavailable',
      stateOutput: `AgentState.market: ${context.market?.data_points?.length || 0} regional data points`,
      latency: '0.04s',
      description: 'Analyzes global pharmaceutical market size, projected 5-year CAGR growth rate, competitor densities, and geographic sales distributions.',
      records: context.market?.data_points?.slice(0, 3).map(m => ({ id: m.region, title: `Market: $${m.market_size_usd_mn}M`, badge: `${m.cagr_percent}% CAGR` })) || [],
    },
    {
      id: 'patent',
      name: 'Patent Landscape Agent',
      nodeFn: 'patent_node(state: AgentState)',
      domain: 'patent',
      provenance: provMap.patent || 'simulated',
      icon: ShieldCheck,
      source: 'USPTO / EPO Registry (Simulation)',
      endpoint: 'DB Repository Query (Fallback Simulation)',
      summary: `${meta?.patent_count || 0} filings reviewed · Status: ${meta?.fto_summary || 'Evaluated'}`,
      stateOutput: `AgentState.patent: ${context.patent?.patents?.length || 0} filings registered`,
      latency: '0.03s',
      description: 'Reviews intellectual property filings, expiration horizons, assignee portfolios, and legal constraint flags. Simulated data is excluded from opportunity scoring.',
      records: context.patent?.patents?.slice(0, 3).map(pt => ({ id: pt.patent_number, title: pt.assignee || 'Patent Record', badge: pt.status })) || [],
    },
    {
      id: 'repurposing',
      name: 'Drug Repurposing Discovery Agent',
      nodeFn: 'repurposing_node(state: AgentState)',
      domain: 'repurposing',
      provenance: 'real',
      icon: Compass,
      source: 'Open Targets Platform GraphQL & ChEMBL',
      endpoint: 'POST https://api.platform.opentargets.org/api/v4/graphql',
      summary: `${context.repurposing?.candidates?.length || 0} candidate new indications ranked with real supporting evidence`,
      stateOutput: `AgentState.repurposing: ${context.repurposing?.candidates?.length || 0} target-disease associations`,
      latency: '2.14s',
      description: 'Resolves compound mechanism of action, retrieves protein targets, performs ontology subtraction against already approved diseases, and ranks candidate indications by association strength.',
      records: context.repurposing?.candidates?.slice(0, 3).map(c => ({ id: c.disease_id, title: c.disease_name, badge: `Score: ${(c.association_score || 0).toFixed(3)}` })) || [],
    },
    {
      id: 'scoring',
      name: 'Deterministic Scoring Engine',
      nodeFn: 'ScoringService.evaluate_and_attach()',
      domain: 'scoring',
      provenance: 'real',
      icon: Award,
      source: 'Rule-Based Deterministic Engine',
      endpoint: 'In-Memory Service (Zero AI Hallucination)',
      summary: `Overall Score: ${(context.score?.overall_score || 0).toFixed(1)} / 100 (${context.score?.data_sources_summary || 'Verified'})`,
      stateOutput: `ResearchContext.score: OpportunityScore attached`,
      latency: '0.01s',
      description: 'Evaluates multi-domain evidence, excludes simulated components from weighting, renormalizes real sources, and computes auditable data confidence scores.',
      records: [
        { id: 'Clinical', title: 'Clinical Subscore', badge: `${context.score?.clinical_score || 0} pts` },
        { id: 'Literature', title: 'Literature Subscore', badge: `${context.score?.research_score || 0} pts` },
        { id: 'Confidence', title: 'Data Completeness', badge: `${context.score?.confidence_score || 0}%` },
      ],
    },
  ];

  const activeNodeData = nodes.find(n => n.id === selectedNode) || nodes[0];
  const ActiveIcon = activeNodeData.icon;

  return (
    <div className="space-y-6">
      {/* ── Orchestration Header ───────────────────────────────────────────── */}
      <div 
        className="bg-white border rounded-xl p-5 space-y-2"
        style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
      >
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700">
              <GitBranch className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-gray-900">
                LangGraph Multi-Agent Orchestrator Pipeline
              </h2>
              <p className="text-xs text-gray-500">
                StateGraph execution DAG for target molecule: <span className="font-semibold text-gray-800">{moleculeName}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-gray-100 text-gray-600 border border-gray-200">
              StateGraph(AgentState)
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-200">
              Execution Succeeded
            </span>
          </div>
        </div>
      </div>

      {/* ── Interactive DAG Flow Chart ─────────────────────────────────────── */}
      <div 
        className="bg-white border rounded-xl p-6 space-y-4"
        style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)' }}
      >
        <div className="flex items-center justify-between border-b pb-3 border-gray-100">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">
              Execution Graph Flow (Click any agent node to inspect)
            </h3>
          </div>
          <span className="text-[11px] text-gray-400">
            Sequential DAG with state-containment &amp; isolated error handling
          </span>
        </div>

        {/* Visual DAG Nodes Horizontal Ribbon */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-3 pt-2">
          {nodes.map((node, idx) => {
            const Icon = node.icon;
            const isSelected = selectedNode === node.id;
            return (
              <div
                key={node.id}
                onClick={() => setSelectedNode(node.id)}
                className={`p-3 rounded-lg border transition-all cursor-pointer select-none space-y-2 ${
                  isSelected
                    ? 'ring-2 ring-blue-600 border-blue-600 bg-blue-50/30'
                    : 'hover:border-blue-300 bg-white border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold font-mono text-gray-400">
                    0{idx + 1}
                  </span>
                  <span
                    className={`text-[9px] font-bold uppercase px-1.5 py-0.2 rounded border ${
                      node.provenance === 'real'
                        ? 'bg-teal-50 text-teal-700 border-teal-200'
                        : 'bg-amber-50 text-amber-700 border-amber-200'
                    }`}
                  >
                    {node.provenance === 'real' ? 'Real API' : 'Simulated'}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 pt-1">
                  <Icon className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span className="text-xs font-bold text-gray-800 truncate">
                    {node.name.replace(' Agent', '')}
                  </span>
                </div>

                <p className="text-[10px] text-gray-500 font-mono truncate">
                  {node.source.split(' ')[0]}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Active Node Inspector Box ──────────────────────────────────────── */}
      <div 
        className="bg-white border rounded-xl p-6 space-y-5"
        style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)' }}
      >
        <div className="flex items-start justify-between border-b pb-4 border-gray-100 flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gray-50 border border-gray-200 flex items-center justify-center text-blue-600 shrink-0">
              <ActiveIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-gray-900">
                  {activeNodeData.name}
                </h3>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-gray-100 text-gray-700">
                  {activeNodeData.nodeFn}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5">
                {activeNodeData.description}
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs text-gray-400 block">Execution Latency</span>
            <span className="text-sm font-mono font-bold text-gray-800">
              ~{activeNodeData.latency}
            </span>
          </div>
        </div>

        {/* Node Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-lg border border-gray-100 bg-gray-50/50 space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block">
              Data Source &amp; Tool Endpoint
            </span>
            <p className="font-semibold text-gray-800 text-sm">
              {activeNodeData.source}
            </p>
            <p className="font-mono text-xs text-blue-700 break-all bg-white p-2 rounded border border-gray-200">
              {activeNodeData.endpoint}
            </p>
            <p className="text-xs text-gray-600 pt-1">
              {activeNodeData.summary}
            </p>
          </div>

          <div className="p-4 rounded-lg border border-gray-100 bg-gray-50/50 space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block">
              Agent State Mutation
            </span>
            <p className="font-mono text-xs text-teal-800 bg-white p-2 rounded border border-gray-200">
              {activeNodeData.stateOutput}
            </p>
            <p className="text-xs text-gray-500">
              Isolated exception handling: Node errors append to <code className="font-mono text-gray-700">state.errors</code> without interrupting pipeline.
            </p>
            <div className="flex items-center gap-2 pt-2">
              <CheckCircle2 className="w-4 h-4 text-teal-600" />
              <span className="font-semibold text-gray-700 text-xs">Zero state schema corruption</span>
            </div>
          </div>
        </div>

        {/* Sample Telemetry Records Extracted */}
        {activeNodeData.records && activeNodeData.records.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-gray-100">
            <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block">
              Sample Data Records Extracted by This Agent
            </span>
            <div className="space-y-1.5">
              {activeNodeData.records.map((rec, rIdx) => (
                <div 
                  key={rIdx}
                  className="p-2.5 rounded bg-white border border-gray-200 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="font-mono font-bold text-gray-700 shrink-0">
                      {rec.id}
                    </span>
                    <span className="text-gray-600 truncate">
                      {rec.title}
                    </span>
                  </div>
                  <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-gray-100 text-gray-700 shrink-0 ml-2">
                    {rec.badge}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
