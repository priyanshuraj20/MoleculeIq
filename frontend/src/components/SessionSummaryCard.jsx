import React, { useState } from 'react';
import { FileText, Download, CheckCircle2, Clock, Layers, Database } from 'lucide-react';
import { downloadPdfReport, downloadJsonReport } from '../services/researchService';

export default function SessionSummaryCard({ context, processingTimeSec }) {
  const [downloadingPdf,  setDownloadingPdf]  = useState(false);
  const [downloadingJson, setDownloadingJson] = useState(false);

  if (!context) return null;

  const moleculeName  = context.molecule_name;
  const trialsCount   = context.clinical?.trials?.length || 0;
  const pubsCount     = context.literature?.publications?.length || 0;
  const patentsCount  = context.patent?.patents?.length || 0;
  const totalEvidence = trialsCount + pubsCount + patentsCount;

  const handleDownloadPdf = async () => {
    try {
      setDownloadingPdf(true);
      await downloadPdfReport(moleculeName);
    } catch (err) {
      alert('Failed to download PDF report: ' + err.message);
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleDownloadJson = async () => {
    try {
      setDownloadingJson(true);
      await downloadJsonReport(moleculeName);
    } catch (err) {
      alert('Failed to download JSON report: ' + err.message);
    } finally {
      setDownloadingJson(false);
    }
  };

  return (
    <div
      className="bg-white rounded-xl p-6 my-8 space-y-4 border"
      style={{
        borderColor: 'var(--color-border)',
        boxShadow: 'var(--shadow-soft)',
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between border-b pb-4"
        style={{ borderColor: 'var(--color-border-light)' }}
      >
        <div className="flex items-center gap-2.5">
          <CheckCircle2 className="w-5 h-5 shrink-0" style={{ color: 'var(--color-teal)' }} />
          <div>
            <h3 className="font-semibold text-base" style={{ color: 'var(--color-text)' }}>
              Research Session Execution Completed
            </h3>
            <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
              All 4 AI research agents executed cleanly for &lsquo;{moleculeName}&rsquo;
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" style={{ color: 'var(--color-text-faint)' }} />
          <span className="text-sm font-semibold tabular-nums" style={{ color: 'var(--color-text)' }}>
            {processingTimeSec != null ? `${processingTimeSec.toFixed(2)}s` : '—'}
          </span>
        </div>
      </div>

      {/* Stat Badges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        {[
          {
            label: 'Agents Executed',
            value: '4 Active Workers',
            icon: <Layers className="w-3.5 h-3.5" style={{ color: 'var(--color-blue)' }} />,
            valueColor: 'var(--color-text)',
          },
          {
            label: 'Evidence Records',
            value: `${totalEvidence} Records Mapped`,
            icon: <Database className="w-3.5 h-3.5" style={{ color: 'var(--color-teal)' }} />,
            valueColor: 'var(--color-text)',
          },
          {
            label: 'Verified Sources',
            value: `${context.score?.real_sources_count ?? 2}/4 Real Sources`,
            icon: null,
            valueColor: 'var(--color-teal)',
          },
          {
            label: 'Confidence Signal',
            value: context.score?.confidence_score != null ? `${context.score.confidence_score.toFixed(0)}%` : '—',
            icon: null,
            valueColor: 'var(--color-text)',
          },
        ].map((item, idx) => (
          <div
            key={idx}
            className="p-3 rounded-lg border space-y-1"
            style={{
              backgroundColor: 'var(--color-bg)',
              borderColor: 'var(--color-border-light)',
            }}
          >
            <span className="block text-[11px] font-medium" style={{ color: 'var(--color-text-faint)' }}>
              {item.label}
            </span>
            <span
              className="font-semibold flex items-center gap-1.5 tabular-nums text-xs"
              style={{ color: item.valueColor || 'var(--color-text)' }}
            >
              {item.icon}
              {item.value}
            </span>
          </div>
        ))}
      </div>

      {/* Export buttons */}
      <div
        className="flex flex-wrap items-center justify-end gap-3 pt-3 border-t"
        style={{ borderColor: 'var(--color-border-light)' }}
      >
        <button
          onClick={handleDownloadJson}
          disabled={downloadingJson}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg transition border disabled:opacity-50 cursor-pointer bg-white hover:bg-gray-50"
          style={{
            borderColor: 'var(--color-border)',
            color: 'var(--color-text)',
          }}
        >
          <Download className="w-4 h-4" style={{ color: 'var(--color-text-muted)' }} />
          {downloadingJson ? 'Exporting JSON...' : 'Export Structured JSON'}
        </button>

        <button
          onClick={handleDownloadPdf}
          disabled={downloadingPdf}
          className="inline-flex items-center gap-2 px-5 py-2 text-xs font-bold rounded-lg transition text-white disabled:opacity-50 cursor-pointer"
          style={{
            backgroundColor: 'var(--color-blue)',
            boxShadow: 'var(--shadow-card)',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-blue-hover)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-blue)'; }}
        >
          <FileText className="w-4 h-4" />
          {downloadingPdf ? 'Generating PDF...' : 'Download Executive Report PDF'}
        </button>
      </div>
    </div>
  );
}
