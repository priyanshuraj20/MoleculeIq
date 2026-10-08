import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  Activity,
  BookOpen,
  TrendingUp,
  ShieldCheck,
  Award,
  Search,
  Send,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Circle,
  GitBranch,
  Scale,
  Download,
  FileCode,
  ExternalLink,
  Compass,
  Clock,
  Copy,
  Check,
  Pill,
  ArrowUpRight,
} from 'lucide-react';

import { useResearch }           from '../hooks/useResearch';
import OverviewCard              from '../components/dashboard/OverviewCard';
import OpportunityCard           from '../components/dashboard/OpportunityCard';
import RepurposingCard          from '../components/dashboard/RepurposingCard';
import ExecutivePreview          from '../components/dashboard/ExecutivePreview';
import AgentOrchestratorView     from '../components/AgentOrchestratorView';
import { downloadPdfReport }     from '../services/pdfService';
import MoleculeIQLogo            from '../components/MoleculeIQLogo';
import ComparisonView            from '../components/ComparisonView';
import ResearchConfidenceCard    from '../components/ResearchConfidenceCard';
import ScoreBreakdownCard        from '../components/ScoreBreakdownCard';
import ResearchTimeline          from '../components/ResearchTimeline';
import SessionSummaryCard        from '../components/SessionSummaryCard';
import MedicineSuggestionsTab    from '../components/dashboard/MedicineSuggestionsTab';

const EXAMPLES = ['Metformin', 'Ibuprofen', 'Pembrolizumab', 'Semaglutide'];

const EVENT_ORDER = [
  'research_started',
  'clinical_started',   'clinical_completed',
  'literature_started', 'literature_completed',
  'market_started',     'market_completed',
  'patent_started',     'patent_completed',
  'repurposing_started','repurposing_completed',
  'aggregation_completed',
  'scoring_completed',
  'research_completed',
];

function isEventAtOrPast(targetEvent, currentEvent, isSuccess) {
  if (isSuccess) return true;
  const targetIdx  = EVENT_ORDER.indexOf(targetEvent);
  const currentIdx = EVENT_ORDER.indexOf(currentEvent);
  if (targetIdx === -1 || currentIdx === -1) return false;
  return currentIdx >= targetIdx;
}

function formatMarketSize(usdMn) {
  if (usdMn == null) return '—';
  if (usdMn >= 1000) return `$${(usdMn / 1000).toFixed(1)}B`;
  return `$${usdMn.toFixed(0)}M`;
}

function deriveOverviewCards(data) {
  if (!data || data.mode === 'comparison' || !data.metadata) return IDLE_CARDS;
  const meta = data.metadata;
  const provMap = meta.provenance_by_domain || {};

  return [
    {
      icon: Activity,
      label: 'Clinical Evidence',
      value: meta.total_trials != null ? `${meta.total_trials} Trials` : '—',
      sub: `${meta.active_trials_count ?? 0} active · ${meta.completed_trials_count ?? 0} completed`,
      source: data.clinical?.source ?? 'ClinicalTrials.gov',
      provenance: data.clinical?.provenance || provMap.clinical || 'real',
      details: [
        { label: 'Total Studies Found',    value: meta.total_trials },
        { label: 'Active / Recruiting',    value: meta.active_trials_count ?? 0 },
        { label: 'Completed Studies',      value: meta.completed_trials_count ?? 0 },
      ],
    },
    {
      icon: BookOpen,
      label: 'Scientific Literature',
      value: meta.total_publications != null ? meta.total_publications.toLocaleString() : '—',
      sub: `${meta.highly_cited_papers_count ?? 0} highly cited publications`,
      source: data.literature?.source ?? 'Europe PMC',
      provenance: data.literature?.provenance || provMap.literature || 'real',
      details: [
        { label: 'Total Indexed Papers',         value: meta.total_publications?.toLocaleString() ?? 0 },
        { label: 'Highly Cited (≥10 citations)', value: meta.highly_cited_papers_count ?? 0 },
      ],
    },
    {
      icon: TrendingUp,
      label: 'Market Intelligence',
      value: formatMarketSize(meta.global_market_size_usd_mn),
      sub: meta.latest_market_cagr != null ? `${meta.latest_market_cagr.toFixed(1)}% CAGR growth` : 'Global sales estimate',
      source: data.market?.source ?? 'IQVIA / Market Models',
      provenance: data.market?.provenance || provMap.market || 'simulated',
      details: [
        { label: 'Global Addressable Market', value: formatMarketSize(meta.global_market_size_usd_mn) },
        { label: '5-Year CAGR',               value: meta.latest_market_cagr != null ? `${meta.latest_market_cagr.toFixed(1)}%` : 'N/A' },
        { label: 'Tracked Regions',           value: meta.market_regions?.slice(0, 3).join(', ') || 'Global' },
      ],
    },
    {
      icon: ShieldCheck,
      label: 'Patent Landscape',
      value: meta.patent_count != null ? `${meta.patent_count} Patents` : '—',
      sub: (meta.fto_summary && meta.fto_summary !== 'No patent data available') ? meta.fto_summary : 'Simulated records',
      source: data.patent?.source ?? 'Patent Registry Database',
      provenance: data.patent?.provenance || provMap.patent || 'simulated',
      details: [
        { label: 'Total Patent Filings', value: meta.patent_count ?? 0 },
        { label: 'Active Filings',       value: meta.active_patents_count ?? 0 },
        { label: 'At-Risk Filings',      value: meta.at_risk_patents_count ?? 0 },
        { label: 'Freedom-To-Operate',   value: meta.fto_summary || 'Analysis Complete' },
      ],
    },
  ];
}

function deriveExecutiveSections(data) {
  if (!data || data.mode === 'comparison' || !data.metadata) return [];
  const meta  = data.metadata;
  const mol   = data.molecule_name;
  const score = data.score;
  const sections = [];

  if (score?.overall_score != null) {
    sections.push({
      title: 'Commercial Opportunity',
      icon: Award,
      content: `${mol} scores ${score.overall_score.toFixed(1)} / 100 on overall commercial viability with ${score.confidence_score?.toFixed(0) || 0}% data confidence. The compound displays ${score.overall_score >= 70 ? 'strong' : 'moderate'} strategic alignment across clinical, market, and intellectual property domains.`,
    });
  }
  if (meta?.total_trials > 0) {
    sections.push({
      title: 'Clinical Insights',
      icon: Activity,
      content: `${mol} has ${meta.total_trials} clinical trial records on file (${meta.active_trials_count ?? 0} active, ${meta.completed_trials_count ?? 0} completed). This reflects ${meta.active_trials_count > 0 ? 'active ongoing clinical validation' : 'established prior clinical studies'}.`,
    });
  }
  if (meta?.global_market_size_usd_mn != null) {
    sections.push({
      title: 'Market Analysis',
      icon: TrendingUp,
      content: `Global addressable market size is estimated at ${formatMarketSize(meta.global_market_size_usd_mn)}${meta.latest_market_cagr != null ? ` with a ${meta.latest_market_cagr.toFixed(1)}% 5-year CAGR` : ''}. ${meta.market_regions?.length > 0 ? `Key regions include ${meta.market_regions.slice(0, 4).join(', ')}.` : ''}`,
    });
  }
  if (meta?.patent_count > 0) {
    sections.push({
      title: 'Patent Landscape & FTO',
      icon: ShieldCheck,
      content: `Patent search identified ${meta.patent_count} filings (${meta.active_patents_count ?? 0} active). FTO Status: ${meta.fto_summary || 'Clean Freedom-To-Operate'}.`,
    });
  }
  if (meta?.total_publications > 0) {
    sections.push({
      title: 'Scientific Momentum',
      icon: BookOpen,
      content: `${meta.total_publications.toLocaleString()} indexed scientific publications on record (${meta.highly_cited_papers_count ?? 0} highly cited), indicating high scientific interest and research momentum.`,
    });
  }
  return sections;
}

const IDLE_CARDS = [
  { icon: Activity,    label: 'Clinical Evidence',     value: '—', sub: 'Run a search to load clinical data.',     source: null },
  { icon: BookOpen,    label: 'Scientific Literature', value: '—', sub: 'Run a search to load publication data.',  source: null },
  { icon: TrendingUp,  label: 'Market Intelligence',   value: '—', sub: 'Run a search to load market data.',       source: null },
  { icon: ShieldCheck, label: 'Patent Landscape',      value: '—', sub: 'Run a search to load patent data.',       source: null },
];

// Individual pipeline step row
function PipelineStep({ label, done, visible, provenance = 'real' }) {
  if (!visible) return null;

  let badgeText = 'Verified';
  let badgeStyle = {
    backgroundColor: '#f0fdfb',
    borderColor: 'var(--color-teal-dim)',
    color: 'var(--color-teal)',
  };

  if (provenance === 'simulated') {
    badgeText = 'Simulated';
    badgeStyle = {
      backgroundColor: '#fffbeb',
      borderColor: '#fde68a',
      color: '#b45309',
    };
  } else if (provenance === 'unavailable') {
    badgeText = 'Unavailable';
    badgeStyle = {
      backgroundColor: '#f3f4f6',
      borderColor: '#e5e7eb',
      color: '#6b7280',
    };
  }

  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-b-0">
      {done ? (
        <CheckCircle2
          className="w-4 h-4 shrink-0"
          style={{ color: provenance === 'simulated' ? '#f59e0b' : 'var(--color-teal)' }}
        />
      ) : (
        <Loader2 className="w-4 h-4 shrink-0 animate-spin" style={{ color: 'var(--color-blue)' }} />
      )}
      <span
        className="text-sm font-medium"
        style={{ color: done ? 'var(--color-text)' : 'var(--color-text-muted)' }}
      >
        {label}
      </span>
      {done && (
        <span
          className="ml-auto text-xs font-medium px-2 py-0.5 rounded border"
          style={badgeStyle}
        >
          {badgeText}
        </span>
      )}
    </div>
  );
}

export default function ResearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery   = searchParams.get('q') ?? '';
  const initialTab     = searchParams.get('tab') || 'overview';

  const [inputVal,    setInputVal]    = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);
  const [activeTab,   setActiveTab]   = useState(initialTab);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [comparatorDrug,   setComparatorDrug]   = useState('');
  const [copiedNctId,      setCopiedNctId]      = useState(null);

  const handleCopyNct = (nctId) => {
    if (!nctId) return;
    navigator.clipboard.writeText(nctId);
    setCopiedNctId(nctId);
    setTimeout(() => setCopiedNctId(null), 2000);
  };

  const { status, statusMessage, lastEvent, data, errorMessage, runResearch, reset } = useResearch();
  const resultsRef = useRef(null);

  const handleResetSearch = () => {
    if (reset) reset();
    setActiveQuery('');
    setInputVal('');
    setSearchParams({});
  };

  const handleTabChange = (newTab) => {
    setActiveTab(newTab);
    const nextParams = new URLSearchParams(searchParams);
    if (newTab === 'overview') {
      nextParams.delete('tab');
    } else {
      nextParams.set('tab', newTab);
    }
    setSearchParams(nextParams);
  };

  useEffect(() => {
    if (initialQuery.trim()) {
      setActiveQuery(initialQuery.trim());
      runResearch(initialQuery.trim());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync tab and search from URL changes (handles browser Back and Forward navigation)
  useEffect(() => {
    const tabFromUrl = searchParams.get('tab') || 'overview';
    if (tabFromUrl !== activeTab) {
      setActiveTab(tabFromUrl);
    }
    const qFromUrl = searchParams.get('q') || '';
    if (qFromUrl && qFromUrl !== activeQuery) {
      setInputVal(qFromUrl);
      setActiveQuery(qFromUrl);
      runResearch(qFromUrl);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  useEffect(() => {
    if (status === 'success' || status === 'error') {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [status]);

  const isLoading = status === 'loading';
  const isSuccess = status === 'success';
  const isError   = status === 'error';
  const isIdle    = status === 'idle' && !activeQuery;

  const isClinicalDone   = isEventAtOrPast('clinical_completed',   lastEvent, isSuccess);
  const isLiteratureDone = isEventAtOrPast('literature_completed', lastEvent, isSuccess);
  const isMarketDone     = isEventAtOrPast('market_completed',     lastEvent, isSuccess);
  const isPatentDone     = isEventAtOrPast('patent_completed',     lastEvent, isSuccess);
  const isRepurposingDone = isEventAtOrPast('repurposing_completed', lastEvent, isSuccess);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const cleaned = inputVal.trim();
    if (cleaned && !isLoading) {
      setActiveQuery(cleaned);
      const nextParams = new URLSearchParams();
      nextParams.set('q', cleaned);
      setSearchParams(nextParams);
      runResearch(cleaned);
    }
  };

  const handleExampleSelect = (mol) => {
    setInputVal(mol);
    setActiveQuery(mol);
    const nextParams = new URLSearchParams();
    nextParams.set('q', mol);
    setSearchParams(nextParams);
    runResearch(mol);
  };

  const handleDownloadPdf = async () => {
    if (!activeQuery) return;
    try {
      setIsDownloadingPdf(true);
      await downloadPdfReport(activeQuery);
    } catch (err) {
      console.error('PDF download error:', err);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const overviewCards     = isSuccess ? deriveOverviewCards(data)     : IDLE_CARDS;
  const executiveSections = isSuccess ? deriveExecutiveSections(data) : [];

  return (
    <div
      className="min-h-[calc(100vh-4rem)] flex flex-col"
      style={{ backgroundColor: 'var(--color-bg)' }}
    >
      <div className="flex-grow max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-32 space-y-8">

        {/* ── Idle welcome state ───────────────────────────────────────────── */}
        {isIdle && (
          <div className="flex flex-col items-center justify-center text-center py-20 space-y-7">
            <MoleculeIQLogo style={{ height: '135px', width: 'auto', display: 'block' }} />
            <div className="space-y-2 max-w-lg mx-auto">
              <h2
                className="text-2xl font-semibold"
                style={{ color: 'var(--color-text)', letterSpacing: '-0.02em' }}
              >
                Pharmaceutical Research Intelligence
              </h2>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-muted)' }}>
                Enter a molecule or drug name to generate an executive research report
                across clinical trials, scientific literature, market data, and patent filings.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2 pt-1">
              <span className="text-xs" style={{ color: 'var(--color-text-faint)' }}>Try:</span>
              {EXAMPLES.map((mol) => (
                <button
                  key={mol}
                  type="button"
                  onClick={() => handleExampleSelect(mol)}
                  className="px-3 py-1 text-xs font-medium border bg-white transition-all cursor-pointer"
                  style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-muted)', borderRadius: '6px' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-blue)';
                    e.currentTarget.style.color = 'var(--color-blue)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                    e.currentTarget.style.color = 'var(--color-text-muted)';
                  }}
                >
                  {mol}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ── Active / In-Progress / Results state ─────────────────────────── */}
        {!isIdle && (
          <div className="space-y-6">

            {/* ── Query header ──────────────────────────────────────────────── */}
            <div
              className="border-b pb-5"
              style={{ borderColor: 'var(--color-border-light)' }}
            >
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                  <p
                    className="text-xs font-medium uppercase tracking-widest mb-1"
                    style={{ color: 'var(--color-text-faint)' }}
                  >
                    Research Query
                  </p>
                  <h2
                    className="text-xl font-semibold"
                    style={{ color: 'var(--color-text)', letterSpacing: '-0.01em' }}
                  >
                    {activeQuery}
                  </h2>
                </div>
                {isSuccess && (
                  <span
                    className="text-xs font-medium px-2.5 py-1 rounded border"
                    style={{
                      backgroundColor: '#f0fdfb',
                      borderColor: 'var(--color-teal-dim)',
                      color: 'var(--color-teal)',
                    }}
                  >
                    Research Complete
                  </span>
                )}
                {isLoading && (
                  <span
                    className="text-xs font-medium px-2.5 py-1 rounded border flex items-center gap-1.5"
                    style={{
                      backgroundColor: '#eff4ff',
                      borderColor: 'var(--color-blue-light)',
                      color: 'var(--color-blue)',
                    }}
                  >
                    <Loader2 className="w-3 h-3 animate-spin" />
                    Analyzing
                  </span>
                )}
              </div>
            </div>

            {/* ── Pipeline status panel (Only shown during active execution, centered) ── */}
            {isLoading && (
              <div className="flex flex-col items-center justify-center py-10 px-4">
                <div
                  className="bg-white rounded-xl border p-6 max-w-lg w-full space-y-4"
                  style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
                >
                  <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: 'var(--color-border-light)' }}>
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700">
                        Multi-Agent LangGraph Pipeline
                      </span>
                      <h3 className="text-base font-semibold text-gray-900 mt-0.5">
                        Researching {activeQuery}
                      </h3>
                    </div>
                    <span
                      className="text-xs font-medium px-2.5 py-1 rounded border flex items-center gap-1.5"
                      style={{
                        backgroundColor: '#eff4ff',
                        borderColor: 'var(--color-blue-light)',
                        color: 'var(--color-blue)',
                      }}
                    >
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Streaming SSE
                    </span>
                  </div>

                  <div className="divide-y divide-gray-100">
                    <PipelineStep
                      label="Clinical Trials Analysis (ClinicalTrials.gov v2)"
                      done={isClinicalDone}
                      visible={true}
                      provenance="real"
                    />
                    <PipelineStep
                      label="Scientific Literature Mining (Europe PMC)"
                      done={isLiteratureDone}
                      visible={isClinicalDone || isLiteratureDone}
                      provenance="real"
                    />
                    <PipelineStep
                      label="Market Intelligence Analysis"
                      done={isMarketDone}
                      visible={isLiteratureDone || isMarketDone}
                      provenance={data?.market?.provenance || "simulated"}
                    />
                    <PipelineStep
                      label="Patent Landscape Registry"
                      done={isPatentDone}
                      visible={isMarketDone || isPatentDone}
                      provenance={data?.patent?.provenance || "simulated"}
                    />
                    <PipelineStep
                      label="Drug Repurposing Discovery (Open Targets + ChEMBL)"
                      done={isRepurposingDone}
                      visible={isPatentDone || isRepurposingDone}
                      provenance="real"
                    />
                    <PipelineStep
                      label="Deterministic Opportunity Synthesis &amp; Scoring"
                      done={isSuccess}
                      visible={isRepurposingDone || isSuccess}
                      provenance="real"
                    />
                  </div>

                  {statusMessage && (
                    <div
                      className="text-xs pt-3 border-t text-gray-500 flex items-center gap-2"
                      style={{ borderColor: 'var(--color-border-light)' }}
                    >
                      <Clock className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                      <span className="truncate">{statusMessage}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ── Error state ───────────────────────────────────────────────── */}
            {isError && (
              <div
                className="border rounded-lg p-5 space-y-3"
                style={{ backgroundColor: '#fff5f5', borderColor: '#fecaca' }}
              >
                <div className="flex items-center gap-2 font-semibold text-sm" style={{ color: '#991b1b' }}>
                  <AlertCircle className="w-4 h-4" style={{ color: '#dc2626' }} />
                  No verified research evidence found
                </div>
                <p className="text-sm leading-relaxed" style={{ color: '#b91c1c' }}>
                  {errorMessage || 'No data was identified across clinical, publication, or patent registries for this query.'}
                </p>
                <div className="pt-2 border-t text-xs" style={{ borderColor: '#fca5a5' }}>
                  <span className="font-medium block mb-2" style={{ color: '#7f1d1d' }}>
                    Suggested pharmaceutical compounds:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {['Semaglutide', 'Tirzepatide', 'Pembrolizumab', 'Metformin', 'Atorvastatin', 'Ibuprofen'].map((s) => (
                      <button
                        key={s}
                        onClick={() => handleExampleSelect(s)}
                        className="px-2.5 py-1 bg-white border rounded text-xs font-medium cursor-pointer"
                        style={{ borderColor: '#fca5a5', color: '#7f1d1d' }}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ── Research results ─────────────────────────────────────────── */}
            {isSuccess && (
              <div ref={resultsRef} className="space-y-6">

                {data?.mode === 'comparison' || data?.data?.molecule_a_name ? (
                  <ComparisonView comparisonData={data?.data || data} onReset={handleResetSearch} />
                ) : (
                  <>
                    {/* ── Tab Navigation Bar ───────────────────────────────────────── */}
                    <div
                      className="flex items-center gap-2 border-b pb-2 overflow-x-auto"
                      style={{ borderColor: 'var(--color-border-light)' }}
                    >
                      <button
                        type="button"
                        onClick={() => handleTabChange('overview')}
                        className={`px-3.5 py-2 text-xs font-semibold rounded-lg border transition-colors cursor-pointer ${
                          activeTab === 'overview'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'bg-transparent border-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                        style={{
                          borderColor: activeTab === 'overview' ? 'var(--color-blue)' : 'transparent',
                        }}
                      >
                        Executive Overview
                      </button>

                      <button
                        type="button"
                        onClick={() => handleTabChange('orchestrator')}
                        className={`px-3.5 py-2 text-xs font-semibold rounded-lg border transition-colors cursor-pointer flex items-center gap-1.5 ${
                          activeTab === 'orchestrator'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'bg-transparent border-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                        style={{
                          borderColor: activeTab === 'orchestrator' ? 'var(--color-blue)' : 'transparent',
                        }}
                      >
                        <GitBranch className="w-3.5 h-3.5" />
                        <span>Agent Orchestration</span>
                        <span className="text-[10px] font-mono px-1 rounded bg-blue-100 text-blue-800">
                          DAG
                        </span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleTabChange('repurposing')}
                        className={`px-3.5 py-2 text-xs font-semibold rounded-lg border transition-colors cursor-pointer flex items-center gap-1.5 ${
                          activeTab === 'repurposing'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'bg-transparent border-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                        style={{
                          borderColor: activeTab === 'repurposing' ? 'var(--color-blue)' : 'transparent',
                        }}
                      >
                        <span>Drug Repurposing</span>
                        {data?.repurposing?.candidates?.length > 0 && (
                          <span
                            className="text-[10px] px-1.5 py-0.2 rounded font-bold"
                            style={{
                              backgroundColor: '#f0fdfb',
                              color: 'var(--color-teal)',
                              border: '1px solid var(--color-teal-dim)',
                            }}
                          >
                            {data.repurposing.candidates.length}
                          </span>
                        )}
                      </button>

                      <button
                        type="button"
                        onClick={() => handleTabChange('evidence')}
                        className={`px-3.5 py-2 text-xs font-semibold rounded-lg border transition-colors cursor-pointer ${
                          activeTab === 'evidence'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'bg-transparent border-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                        style={{
                          borderColor: activeTab === 'evidence' ? 'var(--color-blue)' : 'transparent',
                        }}
                      >
                        Clinical &amp; Evidence
                      </button>

                      <button
                        type="button"
                        onClick={() => handleTabChange('compare')}
                        className={`px-3.5 py-2 text-xs font-semibold rounded-lg border transition-colors cursor-pointer flex items-center gap-1.5 ${
                          activeTab === 'compare'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'bg-transparent border-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                        style={{
                          borderColor: activeTab === 'compare' ? 'var(--color-blue)' : 'transparent',
                        }}
                      >
                        <Scale className="w-3.5 h-3.5" />
                        <span>Head-to-Head Compare</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleTabChange('suggestions')}
                        className={`px-3.5 py-2 text-xs font-semibold rounded-lg border transition-colors cursor-pointer flex items-center gap-1.5 ${
                          activeTab === 'suggestions'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'bg-transparent border-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                        style={{
                          borderColor: activeTab === 'suggestions' ? 'var(--color-blue)' : 'transparent',
                        }}
                      >
                        <Pill className="w-3.5 h-3.5 text-blue-600" />
                        <span>Medicine Suggestions</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleTabChange('exports')}
                        className={`px-3.5 py-2 text-xs font-semibold rounded-lg border transition-colors cursor-pointer flex items-center gap-1.5 ${
                          activeTab === 'exports'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'bg-transparent border-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                        style={{
                          borderColor: activeTab === 'exports' ? 'var(--color-blue)' : 'transparent',
                        }}
                      >
                        <FileCode className="w-3.5 h-3.5" />
                        <span>Session &amp; Exports</span>
                      </button>
                    </div>

                    {/* ── Tab 1: Executive Overview ──────────────────────────────── */}
                    {activeTab === 'overview' && (
                      <div className="space-y-5">
                        {/* Domain Visual Header Banner */}
                        <div 
                          className="bg-white border rounded-xl p-5 flex items-center justify-between flex-wrap gap-4"
                          style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
                        >
                          <div className="flex items-center gap-3.5">
                            <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 shrink-0">
                              <Award className="w-5 h-5" />
                            </div>
                            <div>
                              <h3 className="text-sm font-bold text-gray-900">
                                Executive Commercial Intelligence Synthesis
                              </h3>
                              <p className="text-xs text-gray-500">
                                Multidimensional evaluation across clinical pipelines, indexed scientific literature, market data, and intellectual property.
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-gray-50 border border-gray-200 text-gray-700">
                              Target: {data?.molecule_name || activeQuery}
                            </span>
                            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-teal-50 border border-teal-200 text-teal-700">
                              Score: {data?.score?.overall_score?.toFixed(1) || '—'} / 100
                            </span>
                          </div>
                        </div>

                        {/* 4 stat cards */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {overviewCards.map((card) => (
                            <OverviewCard key={card.label} {...card} isLoading={false} />
                          ))}
                        </div>

                        {/* Opportunity Score + Executive Summary */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          <OpportunityCard
                            score={data?.score}
                            metadata={data?.metadata}
                            isLoading={false}
                          />
                          <ExecutivePreview
                            sections={executiveSections}
                            moleculeName={data?.molecule_name || activeQuery}
                            isLoading={false}
                          />
                        </div>
                      </div>
                    )}

                    {/* ── Tab 2: Agent Orchestration (DAG Graph + Telemetry) ──────── */}
                    {activeTab === 'orchestrator' && (
                      <div className="space-y-5">
                        <AgentOrchestratorView
                          context={data?.data || data}
                          lastEvent={lastEvent}
                        />
                      </div>
                    )}

                    {/* ── Tab 3: Drug Repurposing Discovery ──────────────────────── */}
                    {activeTab === 'repurposing' && (
                      <div className="space-y-5">
                        {/* Domain Visual Header Banner */}
                        <div 
                          className="bg-white border rounded-xl p-5 flex items-center justify-between flex-wrap gap-4"
                          style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
                        >
                          <div className="flex items-center gap-3.5">
                            <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700 shrink-0">
                              <Compass className="w-5 h-5" />
                            </div>
                            <div>
                              <h3 className="text-sm font-bold text-gray-900">
                                Target-Disease Genetics &amp; Repurposing Discovery Studio
                              </h3>
                              <p className="text-xs text-gray-500">
                                Maps biological targets (ChEMBL), subtracts approved disease ontologies (MONDO/EFO), and ranks candidate expansion indications (Open Targets).
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-gray-50 border border-gray-200 text-gray-700">
                              Open Targets &amp; ChEMBL REST
                            </span>
                            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-teal-50 border border-teal-200 text-teal-700">
                              {data?.repurposing?.candidates?.length || 0} Indications Ranked
                            </span>
                          </div>
                        </div>

                        <RepurposingCard
                          repurposing={data?.repurposing}
                          isLoading={isLoading}
                        />
                      </div>
                    )}

                    {/* ── Tab 4: Clinical & Evidence Deep-Dive ───────────────────── */}
                    {activeTab === 'evidence' && (
                      <div className="space-y-6">
                        {/* Domain Visual Header Banner */}
                        <div 
                          className="bg-white border rounded-xl p-5 flex items-center justify-between flex-wrap gap-4"
                          style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
                        >
                          <div className="flex items-center gap-3.5">
                            <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 shrink-0">
                              <Activity className="w-5 h-5" />
                            </div>
                            <div>
                              <h3 className="text-sm font-bold text-gray-900">
                                Clinical Validation &amp; Biomedical Evidence Registry
                              </h3>
                              <p className="text-xs text-gray-500">
                                Verified clinical study records from ClinicalTrials.gov REST API v2 and Europe PMC peer-reviewed publications.
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-gray-50 border border-gray-200 text-gray-700">
                              {data?.metadata?.total_trials || 0} Studies Indexed
                            </span>
                            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-blue-50 border border-blue-200 text-blue-700">
                              {data?.metadata?.total_publications?.toLocaleString() || 0} Papers
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          <ResearchConfidenceCard scoreObj={data?.score} metadata={data?.metadata} />
                          <ScoreBreakdownCard scoreObj={data?.score} />
                        </div>

                        {/* Real Clinical Trials Table */}
                        {data?.clinical?.trials?.length > 0 && (
                          <div 
                            className="bg-white border rounded-xl p-5 space-y-4"
                            style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
                          >
                            <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: 'var(--color-border-light)' }}>
                              <div>
                                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-700">
                                  Verified Clinical Trials (ClinicalTrials.gov)
                                </h3>
                                <p className="text-xs text-gray-500">
                                  Live records returned directly from the official REST API v2
                                </p>
                              </div>
                              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-200">
                                {data.clinical.trials.length} Studies Listed
                              </span>
                            </div>

                            <div className="overflow-x-auto">
                              <table className="w-full text-left text-xs">
                                <thead>
                                  <tr className="border-b text-gray-400 font-semibold uppercase" style={{ borderColor: 'var(--color-border-light)' }}>
                                    <th className="py-2.5 px-3">NCT ID</th>
                                    <th className="py-2.5 px-3">Title / Condition</th>
                                    <th className="py-2.5 px-3">Status</th>
                                    <th className="py-2.5 px-3">Phase</th>
                                    <th className="py-2.5 px-3 text-right">Action</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                  {data.clinical.trials.map((trial, i) => (
                                    <tr key={i} className="hover:bg-gray-50/60 transition-colors">
                                      <td className="py-3 px-3 font-mono font-bold whitespace-nowrap">
                                        <a
                                          href={`https://clinicaltrials.gov/study/${trial.nct_id}`}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="text-blue-700 hover:text-blue-900 hover:underline"
                                          title="Open study record on ClinicalTrials.gov"
                                        >
                                          {trial.nct_id}
                                        </a>
                                      </td>
                                      <td className="py-3 px-3 text-gray-800 font-medium max-w-md">
                                        <div className="line-clamp-2">{trial.title || 'Clinical study record'}</div>
                                        {trial.conditions?.length > 0 && (
                                          <div className="text-[11px] text-gray-400 mt-0.5">
                                            {trial.conditions.slice(0, 2).join(', ')}
                                          </div>
                                        )}
                                      </td>
                                      <td className="py-3 px-3 whitespace-nowrap">
                                        <span className="px-2 py-0.5 rounded text-[11px] font-medium border bg-gray-50 text-gray-700 border-gray-200">
                                          {trial.overall_status || trial.status || 'Active'}
                                        </span>
                                      </td>
                                      <td className="py-3 px-3 whitespace-nowrap text-gray-600 font-medium">
                                        {trial.phase || (trial.phases?.length ? trial.phases.join(', ') : 'Not Specified')}
                                      </td>
                                      <td className="py-3 px-3 text-right whitespace-nowrap">
                                        <div className="inline-flex items-center gap-1.5">
                                          <button
                                            type="button"
                                            onClick={() => handleCopyNct(trial.nct_id)}
                                            className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded border bg-gray-50 hover:bg-gray-100 text-gray-600 transition-colors cursor-pointer"
                                            title="Copy NCT ID"
                                          >
                                            {copiedNctId === trial.nct_id ? (
                                              <>
                                                <Check className="w-3 h-3 text-teal-600" />
                                                <span className="text-teal-700 font-semibold">Copied</span>
                                              </>
                                            ) : (
                                              <>
                                                <Copy className="w-3 h-3 text-gray-400" />
                                                <span>Copy ID</span>
                                              </>
                                            )}
                                          </button>

                                          <a
                                            href={`https://clinicaltrials.gov/study/${trial.nct_id}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium text-[11px] px-2 py-1 rounded border border-blue-100 bg-blue-50/50 hover:bg-blue-50"
                                            title="Open ClinicalTrials.gov study"
                                          >
                                            Registry <ExternalLink className="w-3 h-3" />
                                          </a>

                                          <a
                                            href={`https://pubmed.ncbi.nlm.nih.gov/?term=${trial.nct_id}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1 text-gray-600 hover:text-gray-900 font-medium text-[11px] px-2 py-1 rounded border border-gray-200 bg-white hover:bg-gray-50"
                                            title="Search study on PubMed"
                                          >
                                            PubMed <ExternalLink className="w-3 h-3" />
                                          </a>
                                        </div>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        <ResearchTimeline context={data} />
                      </div>
                    )}

                    {/* ── Tab 5: Head-to-Head Comparative Benchmark ──────────────── */}
                    {activeTab === 'compare' && (
                      <div className="space-y-5">
                        {data?.mode === 'comparison' || data?.data?.molecule_a_name ? (
                          <ComparisonView comparisonData={data?.data || data} onReset={handleResetSearch} />
                        ) : (
                          <div 
                            className="bg-white border rounded-xl p-6 space-y-6"
                            style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
                          >
                            <div className="border-b pb-4 flex items-center justify-between flex-wrap gap-4" style={{ borderColor: 'var(--color-border-light)' }}>
                              <div className="flex items-center gap-3.5">
                                <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700 shrink-0">
                                  <Scale className="w-5 h-5" />
                                </div>
                                <div>
                                  <h3 className="text-sm font-bold text-gray-900">
                                    Head-to-Head Comparative Benchmarking Arena
                                  </h3>
                                  <p className="text-xs text-gray-500">
                                    Dual LangGraph orchestration evaluating differential clinical pipelines, literature citations, and market advantages.
                                  </p>
                                </div>
                              </div>
                              <span className="text-xs font-semibold px-2.5 py-1 rounded bg-gray-50 border border-gray-200 text-gray-700">
                                Comparator Engine
                              </span>
                            </div>

                            <form 
                              onSubmit={(e) => {
                                e.preventDefault();
                                const c = comparatorDrug.trim();
                                if (c && !isLoading) {
                                  const compoundA = data?.molecule_name || activeQuery;
                                  const compQuery = `${compoundA} vs ${c}`;
                                  setActiveQuery(compQuery);
                                  setInputVal(compQuery);
                                  const nextParams = new URLSearchParams();
                                  nextParams.set('q', compQuery);
                                  nextParams.set('tab', 'compare');
                                  setSearchParams(nextParams);
                                  runResearch(compQuery);
                                }
                              }}
                              className="flex items-center gap-3"
                            >
                              <div className="relative flex-grow">
                                <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                                <input
                                  type="text"
                                  value={comparatorDrug}
                                  onChange={(e) => setComparatorDrug(e.target.value)}
                                  placeholder={`Enter competitor drug to benchmark against ${data?.molecule_name || activeQuery}...`}
                                  className="w-full pl-9 pr-3 py-2.5 text-sm border rounded-lg bg-white focus:outline-none"
                                  style={{ borderColor: 'var(--color-border)' }}
                                />
                              </div>
                              <button
                                type="submit"
                                disabled={isLoading || !comparatorDrug.trim()}
                                className="px-5 py-2.5 text-xs font-semibold rounded-lg text-white disabled:opacity-50 cursor-pointer whitespace-nowrap"
                                style={{ backgroundColor: 'var(--color-blue)' }}
                              >
                                {isLoading ? 'Analyzing...' : 'Run Benchmark'}
                              </button>
                            </form>

                            <div className="space-y-2">
                              <span className="text-xs text-gray-400 font-medium">
                                Quick comparator suggestions:
                              </span>
                              <div className="flex flex-wrap gap-2">
                                {['Semaglutide', 'Tirzepatide', 'Pembrolizumab', 'Nivolumab', 'Metformin', 'Ibuprofen']
                                  .filter(item => item.toLowerCase() !== (data?.molecule_name || activeQuery).toLowerCase())
                                  .slice(0, 4)
                                  .map((comp) => (
                                    <button
                                      key={comp}
                                      type="button"
                                      onClick={() => {
                                        setComparatorDrug(comp);
                                        const compoundA = data?.molecule_name || activeQuery;
                                        setActiveQuery(`${compoundA} vs ${comp}`);
                                        runResearch(`${compoundA} vs ${comp}`);
                                      }}
                                      className="px-3 py-1.5 text-xs font-medium rounded-md border bg-gray-50 hover:bg-blue-50 hover:border-blue-300 text-gray-700 transition-colors cursor-pointer"
                                      style={{ borderColor: 'var(--color-border)' }}
                                    >
                                      Compare with {comp}
                                    </button>
                                  ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* ── Tab 6: Medicine & Drug Formulation Suggestions ─────────── */}
                    {activeTab === 'suggestions' && (
                      <MedicineSuggestionsTab molecule={data?.molecule_name || activeQuery} />
                    )}

                    {/* ── Tab 7: Session Execution & Exports ─────────────────────── */}
                    {activeTab === 'exports' && (
                      <div className="space-y-5">
                        {/* Domain Visual Header Banner */}
                        <div 
                          className="bg-white border rounded-xl p-5 flex items-center justify-between flex-wrap gap-4"
                          style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
                        >
                          <div className="flex items-center gap-3.5">
                            <div className="w-10 h-10 rounded-lg bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-700 shrink-0">
                              <FileCode className="w-5 h-5" />
                            </div>
                            <div>
                              <h3 className="text-sm font-bold text-gray-900">
                                Session Governance &amp; Multi-Format Export Dossier
                              </h3>
                              <p className="text-xs text-gray-500">
                                Audit log of orchestrator execution latency, cache status, verified source provenance, and formal dossier downloads.
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-teal-50 border border-teal-200 text-teal-700">
                              Auditable Provenance
                            </span>
                          </div>
                        </div>

                        <SessionSummaryCard context={data} processingTimeSec={data?.processing_time_sec} />

                        {/* Export actions card */}
                        <div 
                          className="bg-white border rounded-xl p-5 space-y-4"
                          style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
                        >
                          <div className="border-b pb-3" style={{ borderColor: 'var(--color-border-light)' }}>
                            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-700">
                              Export Executive Briefing &amp; Agent State
                            </h3>
                            <p className="text-xs text-gray-500">
                              Generate formal dossier or extract raw JSON telemetry
                            </p>
                          </div>

                          <div className="flex flex-wrap gap-3">
                            <button
                              type="button"
                              onClick={handleDownloadPdf}
                              disabled={isDownloadingPdf}
                              className="px-4 py-2 text-xs font-semibold rounded-lg text-white flex items-center gap-2 cursor-pointer disabled:opacity-50"
                              style={{ backgroundColor: 'var(--color-blue)' }}
                            >
                              {isDownloadingPdf ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              ) : (
                                <Download className="w-3.5 h-3.5" />
                              )}
                              <span>Download PDF Briefing</span>
                            </button>

                            <button
                              type="button"
                              onClick={() => {
                                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = `${data?.molecule_name || 'research'}_agent_state.json`;
                                a.click();
                                URL.revokeObjectURL(url);
                              }}
                              className="px-4 py-2 text-xs font-semibold rounded-lg border bg-white hover:bg-gray-50 text-gray-700 flex items-center gap-2 cursor-pointer"
                              style={{ borderColor: 'var(--color-border)' }}
                            >
                              <FileCode className="w-3.5 h-3.5 text-gray-500" />
                              <span>Download AgentState (JSON)</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}

              </div>
            )}

          </div>
        )}

      </div>

      {/* ── Fixed Bottom Input Bar ──────────────────────────────────────────── */}
      <div
        className="fixed bottom-0 left-0 right-0 py-3 px-4 sm:px-6 lg:px-8 z-40 border-t"
        style={{
          backgroundColor: 'rgba(247,249,251,0.97)',
          backdropFilter: 'blur(10px)',
          borderColor: 'var(--color-border)',
        }}
      >
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="relative flex items-center">
            <Search
              className="absolute left-3 w-4 h-4 pointer-events-none"
              style={{ color: 'var(--color-text-faint)' }}
            />
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Enter a molecule or drug name..."
              disabled={isLoading}
              className="w-full pl-9 pr-12 py-2.5 rounded-lg text-sm border transition-all disabled:opacity-60 focus:outline-none bg-white"
              style={{ borderColor: 'var(--color-border)', color: 'var(--color-text)' }}
              onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-blue)'; }}
              onBlur={(e)  => { e.currentTarget.style.borderColor = 'var(--color-border)'; }}
            />
            <button
              type="submit"
              disabled={isLoading || !inputVal.trim()}
              className="absolute right-2 p-2 rounded-md transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              style={{ backgroundColor: 'var(--color-blue)', color: '#ffffff' }}
            >
              {isLoading
                ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                : <Send className="w-3.5 h-3.5" />
              }
            </button>
          </form>
        </div>
      </div>

    </div>
  );
}
