import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import {
  Pill,
  Search,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Activity,
  Layers,
  FlaskConical,
  ExternalLink,
  Info,
  CheckCircle2,
  Clock,
  Atom,
} from 'lucide-react';
import { apiClient } from '../services/apiClient';

const EXAMPLE_MOLECULES = ['Metformin', 'Ibuprofen', 'Semaglutide', 'Pembrolizumab', 'Aspirin'];

export default function MedicalSuggestionPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialMolecule = searchParams.get('q') || searchParams.get('molecule') || '';

  const [inputVal, setInputVal] = useState(initialMolecule);
  const [activeMolecule, setActiveMolecule] = useState(initialMolecule);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (activeMolecule.trim()) {
      fetchSuggestions(activeMolecule.trim());
    }
  }, [activeMolecule]);

  const fetchSuggestions = async (moleculeName) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get('/api/v1/medical-suggestion/', {
        params: { molecule: moleculeName },
      });
      setData(res.data);
    } catch (err) {
      console.error('Failed to fetch medical suggestions:', err);
      setError(
        err.response?.data?.detail ||
          'Could not retrieve medicine suggestions. Please check backend connection and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const clean = inputVal.trim();
    if (clean) {
      setSearchParams({ q: clean });
      setActiveMolecule(clean);
    }
  };

  const handlePickExample = (mol) => {
    setInputVal(mol);
    setSearchParams({ q: mol });
    setActiveMolecule(mol);
  };

  const getStageBadgeStyle = (stage = '') => {
    const s = stage.toLowerCase();
    if (s.includes('approved')) {
      return { bg: '#f0fdf4', text: '#15803d', border: '#bbf7d0' };
    }
    if (s.includes('phase 3') || s.includes('breakthrough')) {
      return { bg: '#eff6ff', text: '#1d4ed8', border: '#bfdbfe' };
    }
    if (s.includes('phase 2') || s.includes('investigational')) {
      return { bg: '#fffbeb', text: '#b45309', border: '#fde68a' };
    }
    return { bg: '#f8fafc', text: '#475569', border: '#e2e8f0' };
  };

  return (
    <div
      className="min-h-[calc(100vh-4.5rem)] px-4 sm:px-6 lg:px-8 py-8 max-w-6xl mx-auto space-y-8"
      style={{ backgroundColor: 'var(--color-bg)' }}
    >
      {/* ── Page Header ────────────────────────────────────────────── */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <span
            className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold"
            style={{
              backgroundColor: '#eff6ff',
              color: 'var(--color-blue)',
              border: '1px solid #bfdbfe',
            }}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Therapeutic Formulation Discovery
          </span>
        </div>
        <h1
          className="text-2xl sm:text-3xl font-bold tracking-tight"
          style={{ color: 'var(--color-text)' }}
        >
          Medicine &amp; Drug Formulation Suggestions
        </h1>
        <p className="text-sm max-w-2xl leading-relaxed" style={{ color: 'var(--color-text-muted)' }}>
          Discover what actual pharmaceutical drugs, modified-release medicines, combination therapeutics,
          and clinical delivery formulations can be manufactured from this target molecule.
        </p>
      </div>

      {/* ── Search Bar ─────────────────────────────────────────────── */}
      <div
        className="bg-white rounded-xl border p-5 shadow-xs space-y-4"
        style={{ borderColor: 'var(--color-border)' }}
      >
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-grow">
            <Search
              className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4"
              style={{ color: 'var(--color-text-faint)' }}
            />
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Enter molecule name (e.g. Metformin, Ibuprofen, Semaglutide)..."
              className="w-full h-11 pl-10 pr-4 rounded-lg border text-sm focus:outline-none transition-colors"
              style={{
                borderColor: 'var(--color-border)',
                color: 'var(--color-text)',
              }}
              onFocus={(e) => (e.target.style.borderColor = 'var(--color-blue)')}
              onBlur={(e) => (e.target.style.borderColor = 'var(--color-border)')}
            />
          </div>
          <button
            type="submit"
            disabled={!inputVal.trim() || loading}
            className="h-11 px-6 rounded-lg text-sm font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer text-white disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
            style={{ backgroundColor: 'var(--color-blue)' }}
          >
            <Sparkles className="w-4 h-4" />
            <span>Generate Suggestions</span>
          </button>
        </form>

        {/* Quick Example Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs font-medium" style={{ color: 'var(--color-text-faint)' }}>
            Try popular molecules:
          </span>
          {EXAMPLE_MOLECULES.map((mol) => (
            <button
              key={mol}
              type="button"
              onClick={() => handlePickExample(mol)}
              className="px-2.5 py-1 text-xs rounded-md border bg-slate-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 transition-colors cursor-pointer"
              style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-muted)' }}
            >
              {mol}
            </button>
          ))}
        </div>
      </div>

      {/* ── Loading State ──────────────────────────────────────────── */}
      {loading && (
        <div className="space-y-4">
          <div className="p-8 text-center bg-white rounded-xl border space-y-3" style={{ borderColor: 'var(--color-border)' }}>
            <div className="w-10 h-10 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <h3 className="text-base font-semibold" style={{ color: 'var(--color-text)' }}>
              Formulating clinical drug profiles for &ldquo;{activeMolecule}&rdquo;...
            </h3>
            <p className="text-xs max-w-md mx-auto" style={{ color: 'var(--color-text-faint)' }}>
              Analyzing chemical scaffold, pharmacokinetics, approved formulations, and translational mechanisms.
            </p>
          </div>
        </div>
      )}

      {/* ── Error State ────────────────────────────────────────────── */}
      {error && !loading && (
        <div className="p-6 bg-red-50 border border-red-200 rounded-xl space-y-2 text-red-700">
          <div className="flex items-center gap-2 font-semibold text-sm">
            <Info className="w-4 h-4 text-red-600" />
            <span>Unable to retrieve drug formulation suggestions</span>
          </div>
          <p className="text-xs">{error}</p>
        </div>
      )}

      {/* ── Results View ───────────────────────────────────────────── */}
      {!loading && data && (
        <div className="space-y-6">
          {/* Summary Box */}
          <div
            className="p-5 bg-white rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Atom className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-bold" style={{ color: 'var(--color-text)' }}>
                  {data.molecule} &mdash; Drug Potential Overview
                </h2>
                <span
                  className="text-[10px] font-semibold px-2 py-0.5 rounded border uppercase tracking-wider"
                  style={{
                    backgroundColor: data.provenance === 'curated_clinical' ? '#f0fdf4' : '#eff6ff',
                    color: data.provenance === 'curated_clinical' ? '#166534' : '#1e40af',
                    borderColor: data.provenance === 'curated_clinical' ? '#bbf7d0' : '#bfdbfe',
                  }}
                >
                  {data.provenance === 'curated_clinical' ? 'Peer-Reviewed' : 'AI Formulation'}
                </span>
              </div>
              <p className="text-xs sm:text-sm leading-relaxed" style={{ color: 'var(--color-text-muted)' }}>
                {data.summary}
              </p>
            </div>

            {/* Link to deep research pipeline */}
            <Link
              to={`/research?q=${encodeURIComponent(data.molecule)}`}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer shrink-0 hover:bg-blue-50 hover:border-blue-300 text-blue-700 bg-white"
              style={{ borderColor: 'var(--color-border)' }}
            >
              <span>Run Deep Research Pipeline</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Formulations Grid */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--color-text-faint)' }}>
                Feasible Medicine Products &amp; Formulations ({data.medicines?.length || 0})
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.medicines?.map((med, index) => {
                const badge = getStageBadgeStyle(med.development_stage);
                return (
                  <div
                    key={index}
                    className="bg-white rounded-xl border p-5 space-y-4 flex flex-col justify-between transition-all hover:shadow-md"
                    style={{ borderColor: 'var(--color-border)' }}
                  >
                    <div className="space-y-3">
                      {/* Top Header */}
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <div
                            className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 border mt-0.5"
                            style={{
                              backgroundColor: '#eff6ff',
                              borderColor: '#dbeafe',
                              color: 'var(--color-blue)',
                            }}
                          >
                            <Pill className="w-4 h-4" />
                          </div>
                          <div>
                            <h4 className="text-sm font-bold leading-snug" style={{ color: 'var(--color-text)' }}>
                              {med.name}
                            </h4>
                            <span className="text-xs font-medium" style={{ color: 'var(--color-text-faint)' }}>
                              {med.dosage_form}
                            </span>
                          </div>
                        </div>

                        <span
                          className="text-[10px] font-semibold px-2 py-0.5 rounded border shrink-0"
                          style={{
                            backgroundColor: badge.bg,
                            color: badge.text,
                            borderColor: badge.border,
                          }}
                        >
                          {med.development_stage}
                        </span>
                      </div>

                      {/* Details Box */}
                      <div className="space-y-2.5 text-xs pt-1">
                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
                          <div className="flex items-center gap-1.5 font-semibold text-slate-700">
                            <Activity className="w-3.5 h-3.5 text-blue-600" />
                            <span>Target Clinical Indication</span>
                          </div>
                          <p className="text-slate-600 pl-5">{med.target_indication}</p>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
                          <div className="flex items-center gap-1.5 font-semibold text-slate-700">
                            <Layers className="w-3.5 h-3.5 text-indigo-600" />
                            <span>Formulation &amp; Action Mechanism</span>
                          </div>
                          <p className="text-slate-600 pl-5 leading-relaxed">{med.mechanism}</p>
                        </div>

                        <div className="p-2.5 rounded-lg bg-emerald-50/60 border border-emerald-100 space-y-1">
                          <div className="flex items-center gap-1.5 font-semibold text-emerald-800">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            <span>Key Clinical &amp; Commercial Advantage</span>
                          </div>
                          <p className="text-emerald-700 pl-5 leading-relaxed">{med.advantage}</p>
                        </div>
                      </div>
                    </div>

                    {/* Bottom Action Footer */}
                    <div className="border-t pt-3 flex items-center justify-between text-xs" style={{ borderColor: 'var(--color-border-light)' }}>
                      <span className="text-slate-400 font-mono">Dose Spec: {med.dosage_form.split('(')[0].trim()}</span>
                      <Link
                        to={`/research?q=${encodeURIComponent(med.name)}`}
                        className="text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center gap-1 cursor-pointer"
                      >
                        <span>Investigate Variant</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ── Empty State ────────────────────────────────────────────── */}
      {!loading && !data && (
        <div className="p-12 text-center bg-white rounded-xl border border-dashed border-gray-200 space-y-3">
          <FlaskConical className="w-10 h-10 mx-auto text-gray-400" />
          <h3 className="text-sm font-semibold text-gray-700">No molecule selected yet</h3>
          <p className="text-xs text-gray-400 max-w-sm mx-auto">
            Type any pharmaceutical molecule or active substance in the search bar above to see what medications can be developed.
          </p>
        </div>
      )}
    </div>
  );
}
