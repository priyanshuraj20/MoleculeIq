import React from 'react';

export default function Footer() {
  return (
    <footer
      className="border-t py-4 px-6 lg:px-10"
      style={{ borderColor: 'var(--color-border)', backgroundColor: '#ffffff' }}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-2">
        <span className="text-xs" style={{ color: 'var(--color-text-faint)' }}>
          © 2024 MoleculeIQ AI. Institutional Grade Intelligence.
        </span>
        <div className="flex items-center gap-5">
          {['Privacy Policy', 'Terms of Service', 'Compliance'].map((link) => (
            <a
              key={link}
              href="#"
              className="text-xs transition-colors"
              style={{ color: 'var(--color-text-faint)' }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-blue)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-faint)'; }}
            >
              {link}
            </a>
          ))}
        </div>
      </div>
    </footer>
  );
}
