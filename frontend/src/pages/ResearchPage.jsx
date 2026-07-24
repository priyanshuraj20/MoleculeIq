import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Activity, BookOpen, TrendingUp, ShieldCheck, Award } from 'lucide-react';

import { useResearch }      from '../hooks/useResearch';
import DashboardHeader      from '../components/dashboard/DashboardHeader';
import SearchSection        from '../components/dashboard/SearchSection';
import OverviewCard         from '../components/dashboard/OverviewCard';
import OpportunityCard      from '../components/dashboard/OpportunityCard';
import ExecutivePreview     from '../components/dashboard/ExecutivePreview';
import ErrorCard            from '../components/dashboard/ErrorCard';

// ─── helpers ──────────────────────────────────────────────────────────────────

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

  const [query, setQuery] = useState(initialQuery);

  const { status, statusMessage, lastEvent, data, errorMessage, runResearch, reset } = useResearch();

  useEffect(() => {
    if (initialQuery.trim()) {
      runResearch(initialQuery.trim());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isLoading = status === 'loading';
  const isSuccess = status === 'success';
  const isError   = status === 'error';

  const handleSubmit = () => {
    if (query.trim()) runResearch(query.trim());
  };

  const handleRetry = () => {
    reset();
    if (query.trim()) runResearch(query.trim());
  };

  const overviewCards     = isSuccess ? deriveOverviewCards(data)     : IDLE_CARDS;
  const executiveSections  = isSuccess ? deriveExecutiveSections(data) : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <DashboardHeader molecule={isSuccess ? data?.molecule_name : (query || null)} />

      {/* ── Search & Progress Panel ─────────────────────────────────────── */}
      <SearchSection
        query={query}
        onQueryChange={setQuery}
        onSubmit={handleSubmit}
        isLoading={isLoading}
        statusMessage={statusMessage}
        lastEvent={lastEvent}
      />

      {/* ── Error card ──────────────────────────────────────────────────── */}
      {isError && (
        <ErrorCard message={errorMessage} onRetry={handleRetry} />
      )}

      {/* ── Overview Cards (Expandable on click) ───────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {overviewCards.map((card) => (
          <OverviewCard
            key={card.label}
            {...card}
            isLoading={isLoading}
          />
        ))}
      </div>

      {/* ── Bottom Row: Opportunity Score + Executive Preview ───────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <OpportunityCard
          score={isSuccess ? data?.score : null}
          metadata={isSuccess ? data?.metadata : null}
          isLoading={isLoading}
        />
        <ExecutivePreview
          sections={executiveSections}
          moleculeName={data?.molecule_name || query || 'Metformin'}
          isLoading={isLoading}
        />
      </div>

    </div>
  );
}
