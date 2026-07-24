import React from 'react';
import { Link } from 'react-router-dom';
import MoleculeIQLogo from './MoleculeIQLogo';

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 py-3 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo & App Title */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <MoleculeIQLogo className="w-8 h-8 shrink-0" />
          <div>
            <div className="font-bold text-slate-900 text-base tracking-tight leading-none">
              Molecule<span className="text-indigo-600">IQ</span>
            </div>
            <p className="text-slate-400 text-xs mt-0.5 font-medium">
              AI-Powered Pharma Intelligence
            </p>
          </div>
        </Link>
      </div>
    </header>
  );
}
