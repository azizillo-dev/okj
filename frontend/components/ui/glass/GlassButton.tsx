'use client';

import React from 'react';
import clsx from 'clsx';

export interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'gold';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Reusable GlassButton with glow effects and ARIA accessibility.
 */
export const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  variant = 'secondary',
  size = 'md',
  className,
  disabled,
  ...props
}) => {
  const sizeClasses = {
    sm: 'px-3.5 py-1.5 text-xs rounded-xl gap-1.5',
    md: 'px-5 py-2.5 text-sm rounded-2xl gap-2',
    lg: 'px-7 py-3.5 text-base rounded-2xl gap-2.5 font-bold',
  }[size];

  const variantClasses = {
    primary:
      'bg-indigo-600/80 hover:bg-indigo-600 text-white border border-indigo-400/30 shadow-[0_4px_20px_rgba(99,102,241,0.3)] hover:shadow-[0_6px_28px_rgba(99,102,241,0.45)]',
    secondary:
      'bg-okj-surface/60 dark:bg-white/[0.08] hover:bg-okj-surface/80 dark:hover:bg-white/[0.14] text-okj-text-primary border border-white/15 backdrop-blur-md shadow-sm',
    ghost:
      'bg-transparent hover:bg-white/[0.06] text-okj-text-secondary hover:text-okj-text-primary border border-transparent',
    gold:
      'bg-gradient-to-r from-okj-gold to-amber-500 text-okj-bg-deep font-display font-black border border-amber-300/40 shadow-[0_4px_20px_rgba(211,168,92,0.35)] hover:shadow-[0_6px_30px_rgba(211,168,92,0.55)]',
  }[variant];

  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center font-display font-medium transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:pointer-events-none select-none relative overflow-hidden',
        sizeClasses,
        variantClasses,
        className
      )}
      disabled={disabled}
      {...props}
    >
      <div className="absolute top-0 inset-x-0 h-px bg-white/25 pointer-events-none" />
      {children}
    </button>
  );
};
