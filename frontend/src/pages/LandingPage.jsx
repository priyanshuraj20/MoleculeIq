import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  BookOpen,
  TrendingUp,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  Search,
} from 'lucide-react';

import ArchitectureDiagram from '../components/landing/ArchitectureDiagram';

// ─── constants ────────────────────────────────────────────────────────────────

const EXAMPLE_MOLECULES = ['Metformin', 'Ibuprofen', 'Pembrolizumab', 'Semaglutide'];

const DOMAINS = [
  {
    icon: Activity,
    title: 'Clinical Evidence',
    description:
      'Track trial phases, recruitment status, lead sponsors, and clinical study outcomes.',
  },
  {
    icon: BookOpen,
    title: 'Scientific Literature',
    description:
      'Analyze peer-reviewed publications, citation metrics, and research momentum.',
  },
  {
    icon: TrendingUp,
    title: 'Market Intelligence',
    description:
      'Evaluate market size, annual CAGR growth, and regional competitor footprints.',
  },
  {
    icon: ShieldCheck,
    title: 'Patent Landscape',
    description:
      'Inspect patent filing status, expiration dates, and Freedom-To-Operate indicators.',
  },
];

// ─── component ────────────────────────────────────────────────────────────────

export default function LandingPage() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const submit = (e) => {
    e.preventDefault();
    navigate(query.trim() ? `/research?q=${encodeURIComponent(query.trim())}` : '/research');
  };

  const pickExample = (mol) => {
    navigate(`/research?q=${encodeURIComponent(mol)}`);
  };

  return (
    <div className="space-y-14 pb-16">

      {/* ── Hero Section ────────────────────────────────────────────────── */}
      <section className="bg-white border-b border-slate-200 py-10 lg:py-14">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-5">

          {/* Badge */}
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-600" />
            Pharmaceutical Research Intelligence
          </span>

          {/* Heading */}
          <div className="space-y-2">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight">
              Molecule<span className="text-indigo-600">IQ</span>
            </h1>
            <p className="text-sm sm:text-base text-slate-600 max-w-xl mx-auto leading-relaxed">
              Consolidate clinical trials, scientific literature, market intelligence,
              and patent landscapes for any pharmaceutical molecule — in one report.
            </p>
          </div>

          {/* Search Input Form */}
          <form onSubmit={submit} className="max-w-lg mx-auto">
            <div className="flex gap-2 p-1.5 bg-white border border-slate-300 rounded-xl shadow-sm focus-within:border-indigo-400 focus-within:ring-1 focus-within:ring-indigo-400 transition-all">
              <div className="relative flex-grow flex items-center">
                <Search className="w-4 h-4 absolute left-3 text-slate-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter a molecule or drug name…"
                  className="w-full pl-9 pr-3 py-2 bg-transparent text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                className="shrink-0 inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none transition-colors"
              >
                Search
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Example Molecule Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 text-xs">
            <span className="text-slate-400 font-medium">Try:</span>
            {EXAMPLE_MOLECULES.map((mol) => (
              <button
                key={mol}
                type="button"
                onClick={() => pickExample(mol)}
                className="px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-slate-600 hover:bg-slate-200 transition-colors font-mono cursor-pointer"
              >
                {mol}
              </button>
            ))}
          </div>

          {/* Value propositions */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-5 text-xs text-slate-600 font-medium border-t border-slate-100">
            {[
              'Multi-Domain Data Synthesis',
              'Commercial Opportunity Analysis',
              'Structured Executive Reports',
            ].map((label) => (
              <div key={label} className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                {label}
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ── Four-Domain Intelligence Section ─────────────────────────────── */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="text-center max-w-lg mx-auto space-y-1.5">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Four-Domain Intelligence
          </h2>
          <p className="text-slate-500 text-xs sm:text-sm">
            Comprehensive data aggregation across key pharmaceutical research domains.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {DOMAINS.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="bg-white rounded-xl p-5 border border-slate-200 hover:border-slate-300 transition-colors space-y-3 shadow-sm"
            >
              <div className="w-9 h-9 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                <Icon className="w-4.5 h-4.5" />
              </div>
              <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
              <p className="text-slate-500 text-xs leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works Section (Product Lifecycle Flow) ───────────────── */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 scroll-mt-24">
        
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-xs font-mono font-semibold text-indigo-600 uppercase tracking-wider bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100">
            Request Lifecycle
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            How MoleculeIQ Works
          </h2>
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-xl mx-auto">
            From a single molecule query to a C-suite executive report in seconds.
          </p>
        </div>

        {/* Clean Product Request Lifecycle Component */}
        <ArchitectureDiagram />

      </section>

    </div>
  );
}
