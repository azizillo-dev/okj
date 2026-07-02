'use client';

import React from 'react';
import clsx from 'clsx';

export interface GlassNavbarProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Reusable GlassNavbar component providing sticky top blur header.
 */
export const GlassNavbar: React.FC<GlassNavbarProps> = ({ children, className }) => {
  return (
    <header
      className={clsx(
        'sticky top-0 z-40 bg-okj-surface/75 dark:bg-[#17233D]/75 backdrop-blur-2xl border-b border-white/10 shadow-lg transition-colors',
        className
      )}
    >
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent pointer-events-none" />
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">{children}</div>
    </header>
  );
};
