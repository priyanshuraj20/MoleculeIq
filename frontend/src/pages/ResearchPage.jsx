import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Activity,
  BookOpen,
  TrendingUp,
  ShieldCheck,
  Award,
  Send,
  Bot,
  User,
  Sparkles,
  Loader2,
  AlertCircle,
  FileText,
  CheckCircle2
} from 'lucide-react';

import { useResearch }      from '../hooks/useResearch';
import OverviewCard         from '../components/dashboard/OverviewCard';
import OpportunityCard      from '../components/dashboard/OpportunityCard';
import ExecutivePreview     from '../components/dashboard/ExecutivePreview';
import ErrorCard            from '../components/dashboard/ErrorCard';
import { downloadPdfReport } from '../services/pdfService';
import MoleculeIQLogo       from '../components/MoleculeIQLogo';
import ComparisonView          from '../components/ComparisonView';
import ResearchConfidenceCard  from '../components/ResearchConfidenceCard';
import ScoreBreakdownCard      from '../components/ScoreBreakdownCard';
import ResearchTimeline        from '../components/ResearchTimeline';
import SessionSummaryCard      from '../components/SessionSummaryCard';

const EXAMPLES = ['Metformin', 'Ibuprofen', 'Pembrolizumab', 'Semaglutide'];

const EVENT_ORDER = [
  'research_started',
  'clinical_started',
  'clinical_completed',
  'literature_started',
  'literature_completed',
  'market_started',
  'market_completed',
  'patent_started',
  'patent_completed',
  'aggregation_completed',
  'scoring_completed',
  'research_completed',
];

function isEventAtOrPast(targetEvent, currentEvent, isSuccess) {
  if (isSuccess) return true;
  const targetIdx = EVENT_ORDER.indexOf(targetEvent);
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
  const meta = data?.metadata;
  if (!meta) return IDLE_CARDS;

  const trialTotal  = meta.total_trials != null ? `${meta.total_trials} Trials` : '—';
  const pubTotal    = meta.total_publications != null ? meta.total_publications.toLocaleString() : '—';
  const marketSize  = formatMarketSize(meta.global_market_size_usd_mn);
  const patentCount = meta.patent_count != null ? `${meta.patent_count} Patents` : '—';

  return [
    {
      icon: Activity,
      label: 'Clinical Evidence',
      value: trialTotal,
      sub: `${meta.active_trials_count ?? 0} active · ${meta.completed_trials_count ?? 0} completed`,
      source: data.clinical?.source ?? null,
      details: [
        { label: 'Total Studies Found', value: meta.total_trials },
        { label: 'Active / Recruiting', value: meta.active_trials_count ?? 0 },
        { label: 'Completed Studies', value: meta.completed_trials_count ?? 0 },
      ],
    },
    {
      icon: BookOpen,
      label: 'Scientific Literature',
      value: pubTotal,
      sub: `${meta.highly_cited_papers_count ?? 0} highly cited publications`,
      source: data.literature?.source ?? null,
      details: [
        { label: 'Total Indexed Papers', value: meta.total_publications?.toLocaleString() ?? 0 },
        { label: 'Highly Cited (≥10 citations)', value: meta.highly_cited_papers_count ?? 0 },
      ],
    },
    {
      icon: TrendingUp,
      label: 'Market Intelligence',
      value: marketSize,
      sub: meta.latest_market_cagr != null ? `${meta.latest_market_cagr.toFixed(1)}% CAGR growth` : 'Global sales data',
      source: data.market?.source ?? null,
      details: [
        { label: 'Global Addressable Market', value: formatMarketSize(meta.global_market_size_usd_mn) },
        { label: '5-Year CAGR', value: meta.latest_market_cagr != null ? `${meta.latest_market_cagr.toFixed(1)}%` : 'N/A' },
        { label: 'Tracked Regions', value: meta.market_regions?.slice(0, 3).join(', ') || 'Global' },
      ],
    },
    {
      icon: ShieldCheck,
      label: 'Patent Landscape',
      value: patentCount,
      sub: meta.fto_summary && meta.fto_summary !== 'No patent data available' ? meta.fto_summary : 'Active filings',
      source: data.patent?.source ?? null,
      details: [
        { label: 'Total Patent Filings', value: meta.patent_count ?? 0 },
        { label: 'Active Filings', value: meta.active_patents_count ?? 0 },
        { label: 'At-Risk Filings', value: meta.at_risk_patents_count ?? 0 },
        { label: 'Freedom-To-Operate', value: meta.fto_summary || 'Analysis Complete' },
      ],
    },
  ];
}

function deriveExecutiveSections(data) {
  if (!data) return [];
  const meta = data.metadata;
  const mol  = data.molecule_name;
  const score = data.score;

  const sections = [];

  if (score?.overall_score != null) {
    sections.push({
      title: 'Commercial Opportunity',
      icon: Award,
      content: `${mol} scores ${score.overall_score.toFixed(1)} / 100 on overall commercial viability with ${score.confidence_score.toFixed(0)}% data confidence. The compound displays ${score.overall_score >= 70 ? 'strong' : 'moderate'} strategic alignment across clinical, market, and intellectual property domains.`,
    });
  }

  if (meta.total_trials > 0) {
    sections.push({
      title: 'Clinical Insights',
      icon: Activity,
      content: `${mol} has ${meta.total_trials} clinical trial records on file (${meta.active_trials_count ?? 0} active, ${meta.completed_trials_count ?? 0} completed). This reflects ${meta.active_trials_count > 0 ? 'active ongoing clinical validation' : 'established prior clinical studies'}.`,
    });
  }

  if (meta.global_market_size_usd_mn != null) {
    sections.push({
      title: 'Market Analysis',
      icon: TrendingUp,
      content: `Global addressable market size is estimated at ${formatMarketSize(meta.global_market_size_usd_mn)}${meta.latest_market_cagr != null ? ` with a ${meta.latest_market_cagr.toFixed(1)}% 5-year CAGR` : ''}. ${meta.market_regions?.length > 0 ? `Key regions include ${meta.market_regions.slice(0, 4).join(', ')}.` : ''}`,
    });
  }

  if (meta.patent_count > 0) {
    sections.push({
      title: 'Patent Landscape & FTO',
      icon: ShieldCheck,
      content: `Patent search identified ${meta.patent_count} filings (${meta.active_patents_count ?? 0} active). FTO Status: ${meta.fto_summary || 'Clean Freedom-To-Operate'}.`,
    });
  }

  if (meta.total_publications > 0) {
    sections.push({
      title: 'Scientific Momentum',
      icon: BookOpen,
      content: `${meta.total_publications.toLocaleString()} indexed scientific publications on record (${meta.highly_cited_papers_count ?? 0} highly cited), indicating high scientific interest and research momentum.`,
    });
  }

  return sections;
}

const IDLE_CARDS = [
  { icon: Activity,    label: 'Clinical Evidence',     value: '—', sub: 'Run a search to load clinical data.', source: null },
  { icon: BookOpen,    label: 'Scientific Literature', value: '—', sub: 'Run a search to load publication data.', source: null },
  { icon: TrendingUp,  label: 'Market Intelligence',   value: '—', sub: 'Run a search to load market data.', source: null },
  { icon: ShieldCheck, label: 'Patent Landscape',      value: '—', sub: 'Run a search to load patent data.', source: null },
];

export default function ResearchPage() {
  const [searchParams] = useSearchParams();
  const initialQuery   = searchParams.get('q') ?? '';

  const [inputVal, setInputVal]     = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);

  const { status, statusMessage, lastEvent, data, errorMessage, runResearch, reset } = useResearch();
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (initialQuery.trim()) {
      setActiveQuery(initialQuery.trim());
      runResearch(initialQuery.trim());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [status, statusMessage, data, errorMessage]);

  const isLoading = status === 'loading';
  const isSuccess = status === 'success';
  const isError   = status === 'error';
  const isIdle    = status === 'idle' && !activeQuery;

  const isClinicalDone   = isEventAtOrPast('clinical_completed', lastEvent, isSuccess);
  const isLiteratureDone = isEventAtOrPast('literature_completed', lastEvent, isSuccess);
  const isMarketDone     = isEventAtOrPast('market_completed', lastEvent, isSuccess);
  const isPatentDone     = isEventAtOrPast('patent_completed', lastEvent, isSuccess);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const cleaned = inputVal.trim();
    if (cleaned && !isLoading) {
      setActiveQuery(cleaned);
      runResearch(cleaned);
    }
  };

  const handleExampleSelect = (mol) => {
    setInputVal(mol);
    setActiveQuery(mol);
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

  const overviewCards    = isSuccess ? deriveOverviewCards(data)     : IDLE_CARDS;
  const executiveSections = isSuccess ? deriveExecutiveSections(data) : [];

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col bg-slate-50/50">

      {/* ── Main Workspace Body ─────────────────────────────────────────────── */}
      <div className="flex-grow max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-28 space-y-6">

        {/* ── Initial Idle State: Welcome Screen (Matches Reference Image 1) ───── */}
        {isIdle && (
          <div className="flex flex-col items-center justify-center text-center py-16 sm:py-24 space-y-6">
            <div className="w-20 h-20 rounded-2xl bg-white border border-slate-200 shadow-md flex items-center justify-center text-indigo-600 mb-2">
              <MoleculeIQLogo className="w-12 h-12" />
            </div>

            <div className="space-y-2 max-w-xl mx-auto">
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Welcome to MoleculeIQ
              </h2>
              <p className="text-sm text-slate-500 leading-relaxed">
                Discover drug repurposing opportunities powered by MoleculeIQ AI analyzing market data, clinical trials, patents, and scientific literature.
              </p>
            </div>

            {/* Quick Example Chips */}
            <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
              <span className="text-xs text-slate-400 font-medium">Try searching:</span>
              {EXAMPLES.map((mol) => (
                <button
                  key={mol}
                  type="button"
                  onClick={() => handleExampleSelect(mol)}
                  className="px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-700 text-xs font-medium hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-600 transition-colors shadow-2xs"
                >
                  {mol}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ── Active Conversation Feed (Matches Reference Image 2) ─────────────── */}
        {!isIdle && (
          <div className="space-y-6">

            {/* User Query Message Bubble */}
            <div className="flex justify-end items-start gap-3">
              <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-xs px-4 py-2.5 text-sm shadow-xs max-w-md font-medium">
                {activeQuery}
              </div>
              <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-xs shrink-0">
                <User className="w-4 h-4" />
              </div>
            </div>

            {/* Master Agent Initial Routing Bubble */}
            <div className="flex justify-start items-start gap-3">
              <div className="w-8 h-8 rounded-xl bg-slate-800 text-white flex items-center justify-center shrink-0 shadow-xs">
                <Bot className="w-4.5 h-4.5" />
              </div>
              <div className="space-y-3 max-w-3xl w-full">
                
                <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 shadow-xs space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-xs text-slate-900">Master Agent</span>
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                  </div>
                  <p className="text-xs text-slate-600">
                    Understood. Orchestrating agents to research your query for <span className="font-semibold text-slate-800">{activeQuery}</span>...
                  </p>

                  {/* Real-time Agent Step-by-Step Progress Cards */}
                  <div className="space-y-2 pt-2 border-t border-slate-100">
                    
                    {/* Clinical Step */}
                    <div className={`flex items-center gap-2 text-xs font-medium ${isClinicalDone ? 'text-emerald-700' : 'text-slate-500'}`}>
                      {isClinicalDone ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      ) : (
                        <Loader2 className="w-4 h-4 animate-spin text-indigo-600 shrink-0" />
                      )}
                      <span>{isClinicalDone ? 'Clinical Analysis Complete' : 'Collecting clinical evidence...'}</span>
                    </div>

                    {/* Literature Step */}
                    {(isClinicalDone || isLiteratureDone) && (
                      <div className={`flex items-center gap-2 text-xs font-medium ${isLiteratureDone ? 'text-emerald-700' : 'text-slate-500'}`}>
                        {isLiteratureDone ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                        ) : (
                          <Loader2 className="w-4 h-4 animate-spin text-indigo-600 shrink-0" />
                        )}
                        <span>{isLiteratureDone ? 'Literature Analysis Complete' : 'Searching scientific literature...'}</span>
                      </div>
                    )}

                    {/* Market Step */}
                    {(isLiteratureDone || isMarketDone) && (
                      <div className={`flex items-center gap-2 text-xs font-medium ${isMarketDone ? 'text-emerald-700' : 'text-slate-500'}`}>
                        {isMarketDone ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                        ) : (
                          <Loader2 className="w-4 h-4 animate-spin text-indigo-600 shrink-0" />
                        )}
                        <span>{isMarketDone ? 'Market Analysis Complete' : 'Analyzing market data...'}</span>
                      </div>
                    )}

                    {/* Patent Step */}
                    {(isMarketDone || isPatentDone) && (
                      <div className={`flex items-center gap-2 text-xs font-medium ${isPatentDone ? 'text-emerald-700' : 'text-slate-500'}`}>
                        {isPatentDone ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                        ) : (
                          <Loader2 className="w-4 h-4 animate-spin text-indigo-600 shrink-0" />
                        )}
                        <span>{isPatentDone ? 'Patent Analysis Complete' : 'Reviewing patent landscape...'}</span>
                      </div>
                    )}

                    {/* Executive Summary Step */}
                    {isPatentDone && (
                      <div className={`flex items-center gap-2 text-xs font-medium ${isSuccess ? 'text-emerald-700' : 'text-indigo-600'}`}>
                        {isSuccess ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                        ) : (
                          <Loader2 className="w-4 h-4 animate-spin text-indigo-600 shrink-0" />
                        )}
                        <span>{isSuccess ? 'Executive Summary & Report Complete' : 'Generating Executive Summary...'}</span>
                      </div>
                    )}

                  </div>
                </div>

                {/* Error State */}
                {isError && (
                  <div className="bg-rose-50/70 border border-rose-200/80 rounded-2xl p-6 shadow-sm my-4 space-y-3">
                    <div className="flex items-center gap-2 text-rose-800 font-bold">
                      <AlertCircle className="w-5 h-5 text-rose-600" />
                      No verified research evidence found
                    </div>
                    <p className="text-sm text-rose-700 leading-relaxed">
                      {errorMessage || 'No data was identified across clinical, publication, or patent registries for this query.'}
                    </p>
                    <div className="pt-2 border-t border-rose-200/50 text-xs text-rose-900">
                      <span className="font-semibold block mb-1">Suggested pharmaceutical compounds:</span>
                      <div className="flex flex-wrap gap-2">
                        {['Semaglutide', 'Tirzepatide', 'Pembrolizumab', 'Metformin', 'Atorvastatin', 'Ibuprofen'].map((s) => (
                          <button
                            key={s}
                            onClick={() => handleExecuteSearch(s)}
                            className="px-2.5 py-1 bg-white hover:bg-rose-100/60 border border-rose-300 rounded-md text-xs text-rose-900 font-medium transition cursor-pointer"
                          >
                            {s}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Results Section (When Success) */}
                {isSuccess && (
                  <div className="space-y-6 pt-2">
                    
                    {/* Check if Comparison Mode */}
                    {data?.mode === 'comparison' || data?.data?.molecule_a_name ? (
                      <ComparisonView comparisonData={data?.data || data} />
                    ) : (
                      <>
                        {/* Overview Cards Grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                          {overviewCards.map((card) => (
                            <OverviewCard key={card.label} {...card} isLoading={false} />
                          ))}
                        </div>

                        {/* Score & Executive Narrative */}
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

                        {/* Research Confidence & Source Availability */}
                        <ResearchConfidenceCard scoreObj={data?.score} metadata={data?.metadata} />

                        {/* Opportunity Score Weight Breakdown */}
                        <ScoreBreakdownCard scoreObj={data?.score} />

                        {/* Chronological Milestone Timeline */}
                        <ResearchTimeline context={data} />
                      </>
                    )}

                    {/* Post-Generation Session Summary & Export Buttons */}
                    <SessionSummaryCard context={data} processingTimeSec={data?.processing_time_sec} />

                  </div>
                )}

              </div>
            </div>

            <div ref={chatEndRef} />
          </div>
        )}

      </div>

      {/* ── Fixed Bottom Prompt Bar (Matches Reference UI Input Bar) ─────────── */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-slate-200 py-3.5 px-4 sm:px-6 lg:px-8 z-40">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="relative flex items-center">
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Ask about drug repurposing opportunities..."
              disabled={isLoading}
              className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={isLoading || !inputVal.trim()}
              className="absolute right-2 p-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </form>
        </div>
      </div>

    </div>
  );
}

