import React from 'react';
import { Link } from 'react-router-dom';
import MoleculeIQLogo from './MoleculeIQLogo';

export default function Navbar() {
  return (
    <header
      className="sticky top-0 z-50 bg-white border-b"
      style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
    >
      <div
        className="w-full flex items-center justify-between px-8 lg:px-12 py-3.5"
      >

        {/* ── Left: Cropped Brand Logo ──────────────────────────── */}
        <Link to="/" className="flex items-center gap-3 select-none shrink-0">
          <MoleculeIQLogo
            style={{ height: '54px', width: 'auto', display: 'block' }}
          />
        </Link>

        {/* ── Right: Clean Login + Register ──────────────────────── */}
        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            style={{
              height: '40px',
              padding: '0 22px',
              fontSize: '14px',
              fontWeight: 500,
              border: '1px solid var(--color-border)',
              borderRadius: '6px',
              backgroundColor: '#ffffff',
              color: 'var(--color-text-muted)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
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
            Log in
          </button>

          <button
            type="button"
            style={{
              height: '40px',
              padding: '0 22px',
              fontSize: '14px',
              fontWeight: 600,
              borderRadius: '6px',
              backgroundColor: 'var(--color-blue)',
              color: '#ffffff',
              cursor: 'pointer',
              border: 'none',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-blue-hover)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-blue)'; }}
          >
            Register
          </button>
        </div>

      </div>
    </header>
  );
}
