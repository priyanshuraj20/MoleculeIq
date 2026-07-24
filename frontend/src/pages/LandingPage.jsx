import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send } from 'lucide-react';
import MoleculeIQLogo from '../components/MoleculeIQLogo';

const EXAMPLE_MOLECULES = ['Metformin', 'Ibuprofen', 'Pembrolizumab', 'Semaglutide'];

export default function LandingPage() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    const cleaned = query.trim();
    navigate(cleaned ? `/research?q=${encodeURIComponent(cleaned)}` : '/research');
  };

  const handlePickExample = (mol) => {
    navigate(`/research?q=${encodeURIComponent(mol)}`);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center bg-white px-4 sm:px-6 lg:px-8 py-12 pb-24">
      <div className="max-w-2xl w-full mx-auto text-center space-y-8">
        
        {/* Centered Logo Icon */}
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-center text-indigo-600">
            <MoleculeIQLogo className="w-10 h-10" />
          </div>
        </div>

        {/* Welcome Title & Short Subtitle */}
        <div className="space-y-3">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
            Welcome to MoleculeIQ
          </h1>
          <p className="text-sm sm:text-base text-slate-500 max-w-lg mx-auto leading-relaxed">
            Discover drug repurposing opportunities powered by MoleculeIQ AI analyzing market data, clinical trials, patents, and scientific literature.
          </p>
        </div>

        {/* Search Prompt Input Bar */}
        <form onSubmit={handleSubmit} className="max-w-xl mx-auto">
          <div className="relative flex items-center shadow-xs">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about drug repurposing opportunities..."
              className="w-full pl-4 pr-12 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
            />
            <button
              type="submit"
              disabled={!query.trim()}
              className="absolute right-2 p-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>

        {/* Example Compound Chips */}
        <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
          <span className="text-xs text-slate-400 font-medium">Try:</span>
          {EXAMPLE_MOLECULES.map((mol) => (
            <button
              key={mol}
              type="button"
              onClick={() => handlePickExample(mol)}
              className="px-3 py-1 rounded-full bg-slate-50 border border-slate-200 text-slate-700 text-xs font-medium hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-600 transition-colors cursor-pointer"
            >
              {mol}
            </button>
          ))}
        </div>

      </div>
    </div>
  );
}
