import React, { useState, useEffect } from 'react';
import { Pill, Sparkles, Activity, Layers, CheckCircle2, Atom, ArrowRight, Loader2, Info } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

export default function MedicineSuggestionsTab({ molecule }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!molecule) return;
    let isMounted = true;

    async function loadSuggestions() {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get('/api/v1/medical-suggestion/', {
          params: { molecule },
        });
        if (isMounted) setData(res.data);
      } catch (err) {
        if (isMounted) {
          setError(
            err.response?.data?.detail ||
              'Unable to load medicine suggestions for this molecule.'
          );
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadSuggestions();

    return () => {
      isMounted = false;
    };
  }, [molecule]);

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

  if (loading) {
    return (
      <div className="bg-white rounded-xl border p-10 text-center space-y-3" style={{ borderColor: 'var(--color-border)' }}>
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
        <h4 className="text-sm font-semibold" style={{ color: 'var(--color-text)' }}>
          Synthesizing Medicine &amp; Drug Formulation Opportunities for &ldquo;{molecule}&rdquo;...
        </h4>
        <p className="text-xs text-gray-500 max-w-md mx-auto">
          Querying clinical pharmacology, drug delivery modalities, and combination therapies.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 space-y-2">
        <div className="flex items-center gap-2 font-semibold text-sm">
          <Info className="w-4 h-4 text-red-600" />
          <span>Could not load medicine formulations</span>
        </div>
        <p className="text-xs">{error}</p>
      </div>
    );
  }

  if (!data || !data.medicines?.length) {
    return (
      <div className="bg-white rounded-xl border p-8 text-center space-y-2" style={{ borderColor: 'var(--color-border)' }}>
        <Pill className="w-8 h-8 text-gray-400 mx-auto" />
        <h4 className="text-sm font-semibold text-gray-700">No specific formulations found</h4>
        <p className="text-xs text-gray-400">No custom manufactured formulations were generated for this query.</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Overview Banner */}
      <div
        className="bg-white rounded-xl border p-5 flex items-start justify-between gap-4 flex-wrap"
        style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
      >
        <div className="space-y-1 max-w-2xl">
          <div className="flex items-center gap-2">
            <Atom className="w-5 h-5 text-blue-600 shrink-0" />
            <h3 className="text-base font-bold" style={{ color: 'var(--color-text)' }}>
              Feasible Medicines &amp; Therapeutics from {data.molecule}
            </h3>
            <span
              className="text-[10px] font-semibold px-2 py-0.5 rounded border uppercase"
              style={{
                backgroundColor: data.provenance === 'curated_clinical' ? '#f0fdf4' : '#eff6ff',
                color: data.provenance === 'curated_clinical' ? '#166534' : '#1e40af',
                borderColor: data.provenance === 'curated_clinical' ? '#bbf7d0' : '#bfdbfe',
              }}
            >
              {data.provenance === 'curated_clinical' ? 'Curated Clinical' : 'AI Formulation'}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">
            {data.summary}
          </p>
        </div>
      </div>

      {/* Formulations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.medicines.map((med, idx) => {
          const badge = getStageBadgeStyle(med.development_stage);
          return (
            <div
              key={idx}
              className="bg-white rounded-xl border p-5 space-y-4 flex flex-col justify-between hover:shadow-md transition-all"
              style={{ borderColor: 'var(--color-border)' }}
            >
              <div className="space-y-3">
                {/* Header */}
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
                      <span className="text-xs font-medium text-gray-500">
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

                {/* Details */}
                <div className="space-y-2 text-xs pt-1">
                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-0.5">
                    <div className="flex items-center gap-1.5 font-semibold text-slate-700">
                      <Activity className="w-3.5 h-3.5 text-blue-600" />
                      <span>Target Indication</span>
                    </div>
                    <p className="text-slate-600 pl-5">{med.target_indication}</p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-0.5">
                    <div className="flex items-center gap-1.5 font-semibold text-slate-700">
                      <Layers className="w-3.5 h-3.5 text-indigo-600" />
                      <span>Formulation Mechanism</span>
                    </div>
                    <p className="text-slate-600 pl-5 leading-relaxed">{med.mechanism}</p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-emerald-50/60 border border-emerald-100 space-y-0.5">
                    <div className="flex items-center gap-1.5 font-semibold text-emerald-800">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Clinical / Commercial Advantage</span>
                    </div>
                    <p className="text-emerald-700 pl-5 leading-relaxed">{med.advantage}</p>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="border-t pt-3 flex items-center justify-between text-xs text-gray-400">
                <span>Dose: {med.dosage_form.split('(')[0].trim()}</span>
                <span className="text-blue-600 font-semibold">{med.development_stage}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
