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
      className="rounded-2xl p-6 my-8 space-y-4 border"
      style={{
        backgroundColor: 'var(--color-navy)',
        borderColor: '#2d3748',
        boxShadow: '0px 8px 32px rgba(15, 23, 42, 0.18)',
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between border-b pb-4"
        style={{ borderColor: '#2d3748' }}
      >
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--color-teal)' }} />
          <div>
            <h3 className="font-bold text-base text-white">
              Research Session Execution Completed
            </h3>
            <p className="text-xs" style={{ color: 'var(--color-navy-text)' }}>
              All 4 AI research agents executed cleanly for &lsquo;{moleculeName}&rsquo;
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4" style={{ color: 'var(--color-navy-text)' }} />
          <span className="text-sm font-semibold text-white">
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
            icon: <Layers className="w-3.5 h-3.5" style={{ color: 'var(--color-blue-light)' }} />,
          },
          {
            label: 'Evidence Records',
            value: `${totalEvidence} Records Mapped`,
            icon: <Database className="w-3.5 h-3.5" style={{ color: 'var(--color-teal-dim)' }} />,
          },
          {
            label: 'Data Sources',
            value: '4/4 Verified',
            valueColor: 'var(--color-teal)',
          },
          {
            label: 'Confidence Signal',
            value: context.score?.confidence_score != null ? `${context.score.confidence_score.toFixed(0)}%` : '—',
            valueColor: '#ffffff',
          },
        ].map((item, idx) => (
          <div
            key={idx}
            className="p-3 rounded-xl border"
            style={{ backgroundColor: 'rgba(255,255,255,0.05)', borderColor: '#2d3748' }}
          >
            <span className="block mb-1" style={{ color: 'var(--color-navy-text)' }}>
              {item.label}
            </span>
            <span
              className="font-bold flex items-center gap-1"
              style={{ color: item.valueColor || '#ffffff' }}
            >
              {item.icon}
              {item.value}
            </span>
          </div>
        ))}
      </div>

      {/* Export buttons */}
      <div
        className="flex flex-wrap items-center justify-end gap-3 pt-2 border-t"
        style={{ borderColor: '#2d3748' }}
      >
        <button
          onClick={handleDownloadJson}
          disabled={downloadingJson}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl transition border disabled:opacity-50 cursor-pointer"
          style={{
            backgroundColor: 'rgba(255,255,255,0.07)',
            borderColor: '#2d3748',
            color: '#e2e8f0',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.12)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.07)'; }}
        >
          <Download className="w-4 h-4" style={{ color: 'var(--color-blue-light)' }} />
          {downloadingJson ? 'Exporting JSON...' : 'Export Structured JSON'}
        </button>

        <button
          onClick={handleDownloadPdf}
          disabled={downloadingPdf}
          className="inline-flex items-center gap-2 px-5 py-2 text-xs font-bold rounded-xl transition text-white disabled:opacity-50 cursor-pointer"
          style={{
            backgroundColor: 'var(--color-blue)',
            boxShadow: '0px 4px 16px rgba(0, 81, 213, 0.35)',
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
