import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
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
} from 'lucide-react';

import { useResearch }           from '../hooks/useResearch';
import OverviewCard              from '../components/dashboard/OverviewCard';
import OpportunityCard           from '../components/dashboard/OpportunityCard';
import ExecutivePreview          from '../components/dashboard/ExecutivePreview';
import { downloadPdfReport }     from '../services/pdfService';
import MoleculeIQLogo            from '../components/MoleculeIQLogo';
import ComparisonView            from '../components/ComparisonView';
import ResearchConfidenceCard    from '../components/ResearchConfidenceCard';
import ScoreBreakdownCard        from '../components/ScoreBreakdownCard';
import ResearchTimeline          from '../components/ResearchTimeline';
import SessionSummaryCard        from '../components/SessionSummaryCard';

const EXAMPLES = ['Metformin', 'Ibuprofen', 'Pembrolizumab', 'Semaglutide'];

const EVENT_ORDER = [
  'research_started',
  'clinical_started',   'clinical_completed',
  'literature_started', 'literature_completed',
  'market_started',     'market_completed',
  'patent_started',     'patent_completed',
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
  const meta = data?.metadata;
  if (!meta) return IDLE_CARDS;

  return [
    {
      icon: Activity,
      label: 'Clinical Evidence',
      value: meta.total_trials != null ? `${meta.total_trials} Trials` : '—',
      sub: `${meta.active_trials_count ?? 0} active · ${meta.completed_trials_count ?? 0} completed`,
      source: data.clinical?.source ?? null,
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
      source: data.literature?.source ?? null,
      details: [
        { label: 'Total Indexed Papers',         value: meta.total_publications?.toLocaleString() ?? 0 },
        { label: 'Highly Cited (≥10 citations)', value: meta.highly_cited_papers_count ?? 0 },
      ],
    },
    {
      icon: TrendingUp,
      label: 'Market Intelligence',
      value: formatMarketSize(meta.global_market_size_usd_mn),
      sub: meta.latest_market_cagr != null ? `${meta.latest_market_cagr.toFixed(1)}% CAGR growth` : 'Global sales data',
      source: data.market?.source ?? null,
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
      sub: meta.fto_summary && meta.fto_summary !== 'No patent data available' ? meta.fto_summary : 'Active filings',
      source: data.patent?.source ?? null,
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
  if (!data) return [];
  const meta  = data.metadata;
  const mol   = data.molecule_name;
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
  { icon: Activity,    label: 'Clinical Evidence',     value: '—', sub: 'Run a search to load clinical data.',     source: null },
  { icon: BookOpen,    label: 'Scientific Literature', value: '—', sub: 'Run a search to load publication data.',  source: null },
  { icon: TrendingUp,  label: 'Market Intelligence',   value: '—', sub: 'Run a search to load market data.',       source: null },
  { icon: ShieldCheck, label: 'Patent Landscape',      value: '—', sub: 'Run a search to load patent data.',       source: null },
];

// Individual pipeline step row
function PipelineStep({ label, done, visible }) {
  if (!visible) return null;
  return (
    <div className="flex items-center gap-3 py-1.5">
      {done ? (
        <CheckCircle2 className="w-4 h-4 shrink-0" style={{ color: 'var(--color-teal)' }} />
      ) : (
        <Loader2 className="w-4 h-4 shrink-0 animate-spin" style={{ color: 'var(--color-blue)' }} />
      )}
      <span
        className="text-sm"
        style={{ color: done ? 'var(--color-text)' : 'var(--color-text-muted)' }}
      >
        {label}
      </span>
      {done && (
        <span
          className="ml-auto text-xs font-medium px-2 py-0.5 rounded border"
          style={{
            backgroundColor: '#f0fdfb',
            borderColor: 'var(--color-teal-dim)',
            color: 'var(--color-teal)',
          }}
        >
          Done
        </span>
      )}
    </div>
  );
}

export default function ResearchPage() {
  const [searchParams] = useSearchParams();
  const initialQuery   = searchParams.get('q') ?? '';

  const [inputVal,    setInputVal]    = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);

  const { status, statusMessage, lastEvent, data, errorMessage, runResearch } = useResearch();
  const resultsRef = useRef(null);

  useEffect(() => {
    if (initialQuery.trim()) {
      setActiveQuery(initialQuery.trim());
      runResearch(initialQuery.trim());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
            <MoleculeIQLogo style={{ height: '110px', width: 'auto', display: 'block' }} />
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

            {/* ── Pipeline status panel (shown while loading or after) ──────── */}
            {(isLoading || isSuccess) && (
              <div
                className="bg-white rounded-lg border p-5"
                style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
              >
                <p
                  className="text-xs font-semibold uppercase tracking-widest mb-4"
                  style={{ color: 'var(--color-text-faint)' }}
                >
                  Research Pipeline
                </p>

                <div
                  className="divide-y"
                  style={{ borderColor: 'var(--color-border-light)' }}
                >
                  <PipelineStep
                    label="Clinical Trials Analysis"
                    done={isClinicalDone}
                    visible={true}
                  />
                  <PipelineStep
                    label="Scientific Literature Analysis"
                    done={isLiteratureDone}
                    visible={isClinicalDone || isLiteratureDone}
                  />
                  <PipelineStep
                    label="Market Intelligence Analysis"
                    done={isMarketDone}
                    visible={isLiteratureDone || isMarketDone}
                  />
                  <PipelineStep
                    label="Patent Landscape Analysis"
                    done={isPatentDone}
                    visible={isMarketDone || isPatentDone}
                  />
                  <PipelineStep
                    label="Executive Summary Generation"
                    done={isSuccess}
                    visible={isPatentDone}
                  />
                </div>

                {isLoading && statusMessage && (
                  <p
                    className="text-xs mt-3 pt-3 border-t"
                    style={{ color: 'var(--color-text-faint)', borderColor: 'var(--color-border-light)' }}
                  >
                    {statusMessage}
                  </p>
                )}
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
              <div ref={resultsRef} className="space-y-5">

                {data?.mode === 'comparison' || data?.data?.molecule_a_name ? (
                  <ComparisonView comparisonData={data?.data || data} />
                ) : (
                  <>
                    {/* 4 stat cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {overviewCards.map((card) => (
                        <OverviewCard key={card.label} {...card} isLoading={false} />
                      ))}
                    </div>

                    {/* Score + Executive */}
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

                    <ResearchConfidenceCard scoreObj={data?.score} metadata={data?.metadata} />
                    <ScoreBreakdownCard     scoreObj={data?.score} />
                    <ResearchTimeline       context={data} />
                  </>
                )}

                <SessionSummaryCard context={data} processingTimeSec={data?.processing_time_sec} />
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
