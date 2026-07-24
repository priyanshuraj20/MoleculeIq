import React from 'react';

/**
 * MoleculeIQLogo
 * Uses the official stitch brand logo PNG.
 */
export default function MoleculeIQLogo({ className = 'w-auto', style }) {
  return (
    <img
      src="/logo.png"
      alt="MoleculeIQ"
      className={className}
      style={style}
      draggable={false}
    />
  );
}
