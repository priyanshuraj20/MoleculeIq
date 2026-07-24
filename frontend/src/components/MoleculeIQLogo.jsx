import React from 'react';

/**
 * MoleculeIQLogo
 * Uses the official stitch brand logo PNG.
 * className controls the display size.
 */
export default function MoleculeIQLogo({ className = 'h-8 w-auto' }) {
  return (
    <img
      src="/logo.png"
      alt="MoleculeIQ"
      className={className}
      draggable={false}
    />
  );
}
