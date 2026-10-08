import React from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export default function BackButton({ className = '' }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const handleBack = () => {
    const q = searchParams.get('q') || '';
    const tab = searchParams.get('tab') || '';

    // 1. If currently in comparison mode ("MoleculeA vs MoleculeB"), go back to MoleculeA
    if (location.pathname === '/research' && q.includes(' vs ')) {
      const primaryMolecule = q.split(' vs ')[0].trim();
      if (primaryMolecule) {
        navigate(`/research?q=${encodeURIComponent(primaryMolecule)}`);
        return;
      }
    }

    // 2. If on research page in a sub-tab (like tab=compare, tab=repurposing, etc.), go back to overview tab
    if (location.pathname === '/research' && tab && tab !== 'overview') {
      const nextParams = new URLSearchParams(searchParams);
      nextParams.delete('tab');
      navigate(`/research?${nextParams.toString()}`);
      return;
    }

    // 3. If on suggestions or report page with a query, go back to research page for that molecule
    if ((location.pathname === '/suggestions' || location.pathname === '/medical-suggestions' || location.pathname === '/report') && q) {
      navigate(`/research?q=${encodeURIComponent(q)}`);
      return;
    }

    // 4. Default: browser history back if available, otherwise safe fallback to Home
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  return (
    <button
      type="button"
      onClick={handleBack}
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border bg-white transition-colors hover:bg-slate-50 cursor-pointer shadow-xs ${className}`}
      style={{
        borderColor: 'var(--color-border)',
        color: 'var(--color-text-muted)',
      }}
      aria-label="Go back"
    >
      <ArrowLeft className="w-3.5 h-3.5" />
      <span>Back</span>
    </button>
  );
}
