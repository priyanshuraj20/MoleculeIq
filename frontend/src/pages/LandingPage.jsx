import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  BookOpen,
  TrendingUp,
  ShieldCheck,
  ArrowRight,
  Github,
  CheckCircle2,
  Search,
  Cpu,
  BarChart3,
  FileText,
  Download
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section */}
      <section className="relative bg-white border-b border-slate-200 py-20 lg:py-28 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            {/* Platform Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse"></span>
              Pharmaceutical Research Intelligence Platform
            </div>

            {/* Title */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 tracking-tight leading-tight">
              Molecule<span className="text-indigo-600">IQ</span>
            </h1>

            {/* Subtitle / Description */}
            <p className="text-lg sm:text-xl text-slate-600 leading-relaxed font-normal">
              Search clinical evidence, scientific literature, market intelligence, and patent insights for pharmaceutical molecules from one unified interface.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link
                to="/research"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-base font-semibold text-white bg-indigo-600 rounded-lg shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all"
              >
                Start Research
                <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="https://github.com/priyanshuraj20/MoleculeIq"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-base font-medium text-slate-700 bg-white border border-slate-300 rounded-lg shadow-sm hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 transition-all"
              >
                <Github className="w-5 h-5" />
                View GitHub
              </a>
            </div>

            {/* Key Value Highlights */}
            <div className="pt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500 font-medium">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Deterministic Scoring Engine
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Real-Time SSE Streaming
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Publication-Ready PDF Reports
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Section — Four Clean Domain Cards */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12 space-y-3">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Four-Domain Intelligence Architecture
          </h2>
          <p className="text-slate-600 text-sm">
            Unified data retrieval and analysis across key pharmaceutical research domains.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Clinical Evidence */}
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <Activity className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Clinical Evidence</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Access real-time clinical trial records from ClinicalTrials.gov. Track development phases, recruitment status, and lead sponsors.
            </p>
          </div>

          {/* Card 2: Scientific Literature */}
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Scientific Literature</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Query peer-reviewed publications from Europe PMC. Analyze publication trends, high-impact citations, and research momentum.
            </p>
          </div>

          {/* Card 3: Market Intelligence */}
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Market Intelligence</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Evaluate global market sizes, annual CAGR growth metrics, and regional competitor footprints for commercial feasibility.
            </p>
          </div>

          {/* Card 4: Patent Landscape */}
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Patent Landscape</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Inspect patent filing statuses, expiration timelines, and Freedom-To-Operate (FTO) constraint risks for generic market entry.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl p-8 lg:p-12 border border-slate-200 shadow-sm space-y-10">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              How MoleculeIQ Works
            </h2>
            <p className="text-slate-600 text-sm">
              End-to-end multi-agent orchestration pipeline from query to downloadable PDF report.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 relative">
            {/* Step 1 */}
            <div className="text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-800 font-bold mx-auto">
                <Search className="w-5 h-5 text-indigo-600" />
              </div>
              <h4 className="font-semibold text-slate-900 text-sm">1. Search Molecule</h4>
              <p className="text-xs text-slate-500">Input target drug or compound name.</p>
            </div>

            {/* Step 2 */}
            <div className="text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-800 font-bold mx-auto">
                <Cpu className="w-5 h-5 text-indigo-600" />
              </div>
              <h4 className="font-semibold text-slate-900 text-sm">2. Research Pipeline</h4>
              <p className="text-xs text-slate-500">LangGraph DAG triggers worker agents.</p>
            </div>

            {/* Step 3 */}
            <div className="text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-800 font-bold mx-auto">
                <BarChart3 className="w-5 h-5 text-indigo-600" />
              </div>
              <h4 className="font-semibold text-slate-900 text-sm">3. Opportunity Score</h4>
              <p className="text-xs text-slate-500">Engine computes commercial sub-scores.</p>
            </div>

            {/* Step 4 */}
            <div className="text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-800 font-bold mx-auto">
                <FileText className="w-5 h-5 text-indigo-600" />
              </div>
              <h4 className="font-semibold text-slate-900 text-sm">4. Executive Report</h4>
              <p className="text-xs text-slate-500">Synthesizes C-suite strategic report.</p>
            </div>

            {/* Step 5 */}
            <div className="text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-800 font-bold mx-auto">
                <Download className="w-5 h-5 text-indigo-600" />
              </div>
              <h4 className="font-semibold text-slate-900 text-sm">5. Download PDF</h4>
              <p className="text-xs text-slate-500">Export publication-ready PDF report.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-indigo-600 rounded-2xl p-8 sm:p-12 text-center text-white space-y-6 shadow-md">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Accelerate Pharmaceutical Research Today
          </h2>
          <p className="text-indigo-100 max-w-xl mx-auto text-sm sm:text-base leading-relaxed">
            Search any molecule to generate instant multi-domain research contexts, opportunity scores, and executive reports.
          </p>
          <div>
            <Link
              to="/research"
              className="inline-flex items-center gap-2 px-6 py-3.5 text-base font-semibold text-indigo-600 bg-white rounded-lg shadow-sm hover:bg-indigo-50 transition-colors"
            >
              Launch Research Portal
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
