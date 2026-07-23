import React from 'react';
import { Atom, Github } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 text-sm border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
                <Atom className="w-4 h-4" />
              </div>
              <span className="font-semibold text-lg text-white tracking-tight">
                Molecule<span className="text-indigo-400">IQ</span>
              </span>
            </div>
            <p className="text-slate-400 max-w-sm text-sm leading-relaxed">
              Pharmaceutical Research Intelligence Platform. Aggregate clinical evidence, literature, market intelligence, and patent landscape insights from a unified interface.
            </p>
          </div>

          {/* Navigation */}
          <div>
            <h4 className="font-semibold text-white text-sm mb-3">Platform</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/research" className="hover:text-white transition-colors">
                  Research Portal
                </Link>
              </li>
              <li>
                <a href="#features" className="hover:text-white transition-colors">
                  Domain Intelligence
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-white transition-colors">
                  Orchestration Pipeline
                </a>
              </li>
            </ul>
          </div>

          {/* Technology */}
          <div>
            <h4 className="font-semibold text-white text-sm mb-3">Technology Stack</h4>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                React
              </span>
              <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                FastAPI
              </span>
              <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                LangGraph
              </span>
              <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Supabase
              </span>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <p>© {new Date().getFullYear()} MoleculeIQ. Built for pharmaceutical research & commercial analysis.</p>
          <div className="flex items-center gap-6">
            <a
              href="https://github.com/priyanshuraj20/MoleculeIq"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 hover:text-white transition-colors"
            >
              <Github className="w-4 h-4" />
              GitHub Repository
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
