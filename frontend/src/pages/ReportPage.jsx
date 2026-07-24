import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FileText,
  Award,
  Activity,
  BookOpen,
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

import { useResearch }        from '../hooks/useResearch';
import { downloadPdfReport }  from '../services/pdfService';
import ReportToolbar          from '../components/report/ReportToolbar';
import ReportMetadataCard     from '../components/report/ReportMetadataCard';
import ReportSidebar          from '../components/report/ReportSidebar';
import ReportSectionCard       from '../components/report/ReportSectionCard';
import ReportToast            from '../components/report/ReportToast';
import ErrorCard              from '../components/dashboard/ErrorCard';

/**
 * Rule-based C-Suite Executive Report Synthesizer.
 * Maps ResearchContext strictly into the 8 standard report sections.
 */
function synthesizeReportSections(context) {
  if (!context) return null;

  const m_name = context.molecule_name;
  const meta   = context.metadata;
  const score  = context.score;

  const ov_score   = score?.overall_score != null ? score.overall_score.toFixed(1) : 'N/A';
  const conf_score = score?.confidence_score != null ? score.confidence_score.toFixed(0) : '100';

  const summary = (
    `Strategic Intelligence Summary for ${m_name}:\n` +
    `${m_name} presents an overall Commercial Opportunity Score of ${ov_score} / 100 with a Data Confidence rating of ${conf_score}%. ` +
    `Analysis across available research domains identifies ${meta.total_trials} total clinical trial(s), ` +
    `${meta.total_publications?.toLocaleString() ?? 0} scientific publication(s), and an FTO assessment of '${meta.fto_summary}'. ` +
    `Research intelligence context was aggregated across ${meta.domains_available?.length ?? 0} available domain datasets.`
  );

  const commercial_opportunity = meta.global_market_size_usd_mn != null
    ? (
        `Commercial Opportunity Evaluation:\n` +
        `The global addressable market is estimated at $${(meta.global_market_size_usd_mn >= 1000 ? (meta.global_market_size_usd_mn / 1000).toFixed(1) + 'B' : meta.global_market_size_usd_mn + 'M')} ` +
        `with a 5-year CAGR growth rate of ${meta.latest_market_cagr?.toFixed(1) ?? '0.0'}%. ` +
        `Commercial footprint spans ${meta.market_regions?.length ?? 0} key market regions (${meta.market_regions?.join(', ') || 'Global'}). ` +
        `Commercial Opportunity Sub-Score: ${score?.market_score?.toFixed(1) ?? 'N/A'} / 100.`
      )
    : `Commercial Opportunity Evaluation:\nNo regional sales or market size records were identified for ${m_name} in primary market datasets. Commercial feasibility remains unconfirmed.`;

  const clinical_analysis = meta.total_trials > 0
    ? (
        `Clinical Development Landscape:\n` +
        `Identified ${meta.total_trials} clinical trial study record(s) registered on ClinicalTrials.gov. ` +
        `Currently, ${meta.active_trials_count ?? 0} trial(s) are actively recruiting or in progress, while ${meta.completed_trials_count ?? 0} trial(s) have reached study completion. ` +
        `Clinical Development Sub-Score: ${score?.clinical_score?.toFixed(1) ?? 'N/A'} / 100.`
      )
    : `Clinical Development Landscape:\nNo registered clinical trial records found for ${m_name} on ClinicalTrials.gov. Clinical safety and efficacy validation remain unconfirmed.`;

  const scientific_analysis = meta.total_publications > 0
    ? (
        `Scientific Literature & Research Momentum:\n` +
        `Identified ${meta.total_publications.toLocaleString()} indexed scientific publication(s) in PubMed / Europe PMC repository. ` +
        `Includes ${meta.highly_cited_papers_count ?? 0} high-impact highly cited publication(s) (>=10 citations), reflecting strong research momentum. ` +
        `Scientific Research Sub-Score: ${score?.research_score?.toFixed(1) ?? 'N/A'} / 100.`
      )
    : `Scientific Literature:\nNo peer-reviewed scientific publications identified for ${m_name} in Europe PMC.`;

  const market_analysis = meta.market_regions?.length > 0
    ? (
        `Market Intelligence & Regional Footprint:\n` +
        `Commercial sales records identified across ${meta.market_regions.length} key geographic market region(s). ` +
        `Global valuation stands at $${(meta.global_market_size_usd_mn >= 1000 ? (meta.global_market_size_usd_mn / 1000).toFixed(1) + 'B' : meta.global_market_size_usd_mn + 'M')}. ` +
        `Market Feasibility Sub-Score: ${score?.market_score?.toFixed(1) ?? 'N/A'} / 100.`
      )
    : `Market Intelligence:\nMarket intelligence data unavailable for ${m_name}. Primary commercial research is recommended prior to market entry.`;

  const patent_analysis = meta.patent_count > 0
    ? (
        `Patent Landscape & Freedom-To-Operate (FTO):\n` +
        `Freedom-To-Operate Assessment: '${meta.fto_summary}'. ` +
        `Identified ${meta.patent_count} total patent filing(s), including ${meta.active_patents_count ?? 0} active patent(s) in force ` +
        `and ${meta.at_risk_patents_count ?? 0} active legal constraint(s). ` +
        `Patent Landscape Sub-Score: ${score?.patent_score?.toFixed(1) ?? 'N/A'} / 100.`
      )
    : `Patent Landscape:\nNo patent filings registered in patent databases for ${m_name}. FTO status remains unconfirmed.`;

  const risks_list = [];
  if (meta.at_risk_patents_count > 0) {
    risks_list.push(`• Intellectual Property Risk: ${meta.at_risk_patents_count} active patent constraint(s) present potential FTO blocking risks.`);
  }
  if ((meta.active_trials_count ?? 0) === 0) {
    risks_list.push('• Clinical Pipeline Risk: Zero active recruiting clinical trials detected.');
  }
  if (!meta.global_market_size_usd_mn) {
    risks_list.push('• Market Risk: Unconfirmed global sales volume in primary databases.');
  }
  if (risks_list.length === 0) {
    risks_list.push('• Low Strategic Risk: No major blocking constraints identified across available datasets.');
  }
  const risks = risks_list.join('\n\n');

  let recommendation = '';
  const overall = score?.overall_score ?? 0;
  if (overall >= 70.0) {
    recommendation = `Investment Recommendation: HIGH OPPORTUNITY (Score: ${ov_score} / 100).\nProceed with advanced commercial entry planning, active licensing, and formulation development. The target molecule exhibits strong multi-domain validation.`;
  } else if (overall >= 40.0) {
    recommendation = `Investment Recommendation: MODERATE OPPORTUNITY (Score: ${ov_score} / 100).\nConduct targeted FTO legal review and competitive positioning analysis prior to capital commitment.`;
  } else {
    recommendation = `Investment Recommendation: HIGH UNCERTAINTY / LOW PRIORITY (Score: ${ov_score} / 100).\nData coverage is limited; requires additional primary data validation before resource allocation.`;
  }

  return {
    summary,
    commercial_opportunity,
    clinical_analysis,
    scientific_analysis,
    market_analysis,
    patent_analysis,
    risks,
    recommendation,
  };
}

export default function ReportPage() {
  const [searchParams] = useSearchParams();
  const moleculeQuery = searchParams.get('q') || 'Metformin';

  const { status, statusMessage, data, errorMessage, runResearch } = useResearch();

  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [toastState, setToastState]             = useState(null); // { type, message }

  useEffect(() => {
    if (moleculeQuery) {
      runResearch(moleculeQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [moleculeQuery]);

  const isLoading = status === 'loading';
  const isError   = status === 'error';
  const isSuccess = status === 'success';

  const report = isSuccess ? synthesizeReportSections(data) : null;
  const activeMolecule = data?.molecule_name || moleculeQuery;

  // PDF Export Handler (Session 22)
  const handleDownloadPdf = async () => {
    if (isDownloadingPdf || !activeMolecule) return;

    setIsDownloadingPdf(true);
    setToastState(null);

    try {
      const filename = await downloadPdfReport(activeMolecule);
      setToastState({
        type: 'success',
        message: `Executive Report downloaded successfully (${filename}).`,
      });
      // Auto-hide success toast after 4 seconds
      setTimeout(() => setToastState(null), 4000);
    } catch (err) {
      setToastState({
        type: 'error',
        message: err.message || 'Failed to download PDF report. Please try again.',
      });
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  return (
    <div className="min-h-screen pb-16 space-y-6" style={{ backgroundColor: 'var(--color-bg)' }}>

      {/* ── Top Sticky Toolbar ──────────────────────────────────────────── */}
      <ReportToolbar
        moleculeName={activeMolecule}
        generatedTime={data?.created_at ? new Date(data.created_at).toLocaleString() : null}
        onDownloadPdf={handleDownloadPdf}
        isDownloading={isDownloadingPdf}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

        {/* ── Toast Notification for PDF Download Feedback ───────── */}
        {toastState && (
          <ReportToast
            type={toastState.type}
            message={toastState.message}
            onClose={() => setToastState(null)}
            onRetry={toastState.type === 'error' ? handleDownloadPdf : undefined}
          />
        )}

        {/* ── Error card for pipeline errors ────────────────────────────── */}
        {isError && (
          <ErrorCard message={errorMessage} onRetry={() => runResearch(moleculeQuery)} />
        )}

        {/* ── Loading Spinner for pipeline research ────────────────────── */}
        {isLoading && (
          <div className="bg-white rounded-xl border p-12 text-center space-y-3" style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-soft)' }}>
            <Loader2 className="w-8 h-8 animate-spin mx-auto" style={{ color: 'var(--color-blue)' }} />
            <p className="text-sm font-medium" style={{ color: 'var(--color-text)' }}>Synthesizing Executive Report…</p>
            <p className="text-xs" style={{ color: 'var(--color-text-faint)' }}>{statusMessage}</p>
          </div>
        )}

        {/* ── Success Report Workspace ──────────────────────────────────── */}
        {isSuccess && report && (
          <>
            {/* Metadata Header Cards */}
            <ReportMetadataCard
              moleculeName={data.molecule_name}
              overallScore={data.score?.overall_score}
              confidenceScore={data.score?.confidence_score}
              generatedDate={data.created_at}
              status="Completed"
            />

            {/* Layout: Main Content (75%) + Table of Contents Sidebar (25%) */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

              {/* Sidebar Table of Contents */}
              <div className="hidden lg:block lg:col-span-1">
                <ReportSidebar />
              </div>

              {/* Main Report Document */}
              <main className="lg:col-span-3 space-y-6">
                <ReportSectionCard
                  id="summary"
                  title="Executive Summary"
                  icon={FileText}
                  content={report.summary}
                />

                <ReportSectionCard
                  id="commercial"
                  title="Commercial Opportunity"
                  icon={Award}
                  content={report.commercial_opportunity}
                />

                <ReportSectionCard
                  id="clinical"
                  title="Clinical Landscape"
                  icon={Activity}
                  content={report.clinical_analysis}
                />

                <ReportSectionCard
                  id="scientific"
                  title="Scientific Literature"
                  icon={BookOpen}
                  content={report.scientific_analysis}
                />

                <ReportSectionCard
                  id="market"
                  title="Market Intelligence"
                  icon={TrendingUp}
                  content={report.market_analysis}
                />

                <ReportSectionCard
                  id="patent"
                  title="Patent Landscape"
                  icon={ShieldCheck}
                  content={report.patent_analysis}
                />

                <ReportSectionCard
                  id="risks"
                  title="Risk Assessment"
                  icon={AlertTriangle}
                  content={report.risks}
                />

                <ReportSectionCard
                  id="recommendation"
                  title="Final Recommendation"
                  icon={CheckCircle2}
                  content={report.recommendation}
                  isHighlighted
                />
              </main>

            </div>
          </>
        )}

      </div>
    </div>
  );
}
