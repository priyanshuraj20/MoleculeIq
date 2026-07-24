import React from 'react';

/**
 * MoleculeIQLogo
 * Clean vector logo for MoleculeIQ inspired by pharma intelligence branding.
 */
export default function MoleculeIQLogo({ className = "w-8 h-8" }) {
  return (
    <svg
      className={className}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="40" height="40" rx="10" fill="#4F46E5" />
      {/* Molecular node structure */}
      <circle cx="14" cy="14" r="3.5" fill="white" />
      <circle cx="26" cy="14" r="3.5" fill="white" />
      <circle cx="20" cy="26" r="4" fill="#A5B4FC" />
      <path
        d="M14 14L20 26M26 14L20 26M14 14H26"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}
