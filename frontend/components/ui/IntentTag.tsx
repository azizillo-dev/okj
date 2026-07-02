'use client';

import React from 'react';
import clsx from 'clsx';

interface IntentTagProps {
  type: string;
  active?: boolean;
  onClick?: () => void;
  className?: string;
}

export const IntentTag: React.FC<IntentTagProps> = ({ type, active = false, onClick, className }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        'inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-display font-medium transition-all duration-200 select-none cursor-pointer shrink-0',
        active
          ? 'bg-okj-gold text-okj-bg-deep font-bold shadow-sm shadow-okj-gold/30'
          : 'bg-okj-surface text-okj-text-secondary hover:text-okj-text-primary hover:bg-okj-card border border-okj-card-border/50',
        className
      )}
    >
      {type}
    </button>
  );
};
