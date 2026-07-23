import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Atom, Github, ArrowRight } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm group-hover:bg-indigo-700 transition-colors">
            <Atom className="w-5 h-5" />
          </div>
          <span className="font-semibold text-lg text-slate-900 tracking-tight">
            Molecule<span className="text-indigo-600">IQ</span>
          </span>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
          <Link
            to="/research"
            className={`transition-colors hover:text-slate-900 ${
              location.pathname === '/research' ? 'text-indigo-600 font-semibold' : ''
            }`}
          >
            Research
          </Link>
          <a href="#features" className="transition-colors hover:text-slate-900">
            Features
          </a>
          <a href="#how-it-works" className="transition-colors hover:text-slate-900">
            How It Works
          </a>
          <a
            href="https://github.com/priyanshuraj20/MoleculeIq"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 transition-colors hover:text-slate-900"
          >
            <Github className="w-4 h-4" />
            GitHub
          </a>
        </nav>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          <Link
            to="/research"
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all"
          >
            Start Research
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </header>
  );
}
