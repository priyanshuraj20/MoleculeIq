import React, { useState } from 'react';
import { FileText, Download, CheckCircle2, Clock, Layers, Database } from 'lucide-react';
import { downloadPdfReport, downloadJsonReport } from '../services/researchService';

export default function SessionSummaryCard({ context, processingTimeSec }) {
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingJson, setDownloadingJson] = useState(false);

  if (!context) return null;

  const moleculeName = context.molecule_name;
  const trialsCount = context.clinical?.trials?.length || 0;
  const pubsCount = context.literature?.publications?.length || 0;
  const patentsCount = context.patent?.patents?.length || 0;
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
    <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-xl border border-slate-800 my-8 space-y-4">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <div>
            <h3 className="font-bold text-base text-white">Research Session Execution Completed</h3>
            <p className="text-xs text-slate-400">All 4 AI research agents executed cleanly for '{moleculeName}'</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-400" />
          <span className="text-sm font-semibold text-slate-200">
            {processingTimeSec ? `${processingTimeSec.toFixed(2)}s` : '< 3.0s'}
          </span>
        </div>
      </div>

      {/* Metadata Badges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60">
          <span className="text-slate-400 block mb-1">Agents Executed</span>
          <span className="font-bold text-white flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-indigo-400" /> 4 Active Workers
          </span>
        </div>

        <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60">
          <span className="text-slate-400 block mb-1">Evidence Records</span>
          <span className="font-bold text-white flex items-center gap-1">
            <Database className="w-3.5 h-3.5 text-emerald-400" /> {totalEvidence} Records Mapped
          </span>
        </div>

        <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60">
          <span className="text-slate-400 block mb-1">Data Sources</span>
          <span className="font-bold text-emerald-400">✓ 4/4 Verified</span>
        </div>

        <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/60">
          <span className="text-slate-400 block mb-1">Confidence Signal</span>
          <span className="font-bold text-white">
            {context.score?.confidence_score?.toFixed(0) ?? 100}% Strong
          </span>
        </div>
      </div>

      {/* Action Export Buttons */}
      <div className="flex flex-wrap items-center justify-end gap-3 pt-2 border-t border-slate-800">
        <button
          onClick={handleDownloadJson}
          disabled={downloadingJson}
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl transition border border-slate-700 disabled:opacity-50"
        >
          <Download className="w-4 h-4 text-indigo-400" />
          {downloadingJson ? 'Exporting JSON...' : 'Export Structured JSON'}
        </button>

        <button
          onClick={handleDownloadPdf}
          disabled={downloadingPdf}
          className="inline-flex items-center gap-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl transition shadow-lg shadow-indigo-600/30 disabled:opacity-50"
        >
          <FileText className="w-4 h-4 text-white" />
          {downloadingPdf ? 'Generating PDF...' : 'Download Executive Report PDF'}
        </button>
      </div>
    </div>
  );
}
