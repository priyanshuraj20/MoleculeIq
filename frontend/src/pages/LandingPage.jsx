import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ArrowRight, Shield } from 'lucide-react';
import MoleculeIQLogo from '../components/MoleculeIQLogo';
import { useAuth } from '../auth/useAuth';
import GoogleLoginButton from '../auth/GoogleLoginButton';

const EXAMPLE_MOLECULES = ['Metformin', 'Ibuprofen', 'Pembrolizumab', 'Semaglutide'];

export default function LandingPage() {
  const [query, setQuery] = useState('');
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    const cleaned = query.trim();
    if (cleaned) {
      navigate(`/research?q=${encodeURIComponent(cleaned)}`);
    }
  };

  const handlePickExample = (mol) => {
    navigate(`/research?q=${encodeURIComponent(mol)}`);
  };

  return (
    <div
      className="min-h-[calc(100vh-4.5rem)] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 py-12 pb-24"
      style={{ backgroundColor: 'var(--color-bg)' }}
    >
      <div className="max-w-2xl w-full mx-auto text-center space-y-8">

        {/* Center Logo — prominent and clear */}
        <div className="flex justify-center py-2">
          <MoleculeIQLogo style={{ height: '100px', width: 'auto', display: 'block' }} />
        </div>

        {/* Heading */}
        <div className="space-y-3">
          <h1
            className="text-3xl sm:text-4xl font-bold"
            style={{ color: 'var(--color-text)', letterSpacing: '-0.02em' }}
          >
            Welcome to MoleculeIQ
          </h1>
          <p
            className="text-base max-w-lg mx-auto leading-relaxed"
            style={{ color: 'var(--color-text-muted)' }}
          >
            Discover drug repurposing opportunities powered by AI analyzing
            market data, clinical trials, patents, and scientific literature.
          </p>
        </div>

        {/* Auth prompt if not logged in */}
        {!isAuthenticated ? (
          <div className="max-w-md mx-auto p-6 bg-white border rounded-xl shadow-sm space-y-4" style={{ borderColor: 'var(--color-border)' }}>
            <div className="flex items-center justify-center gap-2 text-sm font-semibold" style={{ color: 'var(--color-text)' }}>
              <Shield className="w-4 h-4" style={{ color: 'var(--color-blue)' }} />
              Sign in with Google to start research
            </div>
            <p className="text-xs" style={{ color: 'var(--color-text-faint)' }}>
              Access AI research pipelines, opportunity scores, and executive PDF reports.
            </p>
            <div className="flex justify-center pt-1">
              <GoogleLoginButton />
            </div>
          </div>
        ) : (
          /* Search Bar for authenticated users */
          <form onSubmit={handleSubmit} className="max-w-xl mx-auto">
            <div
              className="relative flex items-center bg-white border transition-all"
              style={{
                borderColor: 'var(--color-border)',
                boxShadow: 'var(--shadow-soft)',
                borderRadius: '8px',
              }}
            >
              <Search
                className="absolute left-4 w-4 h-4 pointer-events-none shrink-0"
                style={{ color: 'var(--color-text-faint)' }}
              />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter a molecule or drug name..."
                className="w-full h-12 pl-11 pr-12 bg-transparent text-sm focus:outline-none"
                style={{ color: 'var(--color-text)', borderRadius: '8px' }}
                onFocus={(e) => { e.currentTarget.parentElement.style.borderColor = 'var(--color-blue)'; }}
                onBlur={(e)  => { e.currentTarget.parentElement.style.borderColor = 'var(--color-border)'; }}
              />
              <button
                type="submit"
                disabled={!query.trim()}
                className="absolute right-2 w-8 h-8 flex items-center justify-center transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                style={{ backgroundColor: 'var(--color-blue)', color: '#ffffff', borderRadius: '6px' }}
                onMouseEnter={(e) => { if (!e.currentTarget.disabled) e.currentTarget.style.backgroundColor = 'var(--color-blue-hover)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-blue)'; }}
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        )}

        {/* Example chips */}
        <div className="flex flex-wrap items-center justify-center gap-2">
          <span
            className="text-xs font-medium"
            style={{ color: 'var(--color-text-faint)' }}
          >
            Try:
          </span>
          {EXAMPLE_MOLECULES.map((mol) => (
            <button
              key={mol}
              type="button"
              onClick={() => handlePickExample(mol)}
              className="px-3.5 py-1.5 bg-white text-xs font-medium border transition-all cursor-pointer"
              style={{
                borderColor: 'var(--color-border)',
                color: 'var(--color-text-muted)',
                borderRadius: '6px',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-blue)';
                e.currentTarget.style.color = 'var(--color-blue)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-border)';
                e.currentTarget.style.color = 'var(--color-text-muted)';
              }}
            >
              {mol}
            </button>
          ))}
        </div>

      </div>
    </div>
  );
}
