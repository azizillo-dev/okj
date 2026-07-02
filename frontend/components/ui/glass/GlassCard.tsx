'use client';

import React from 'react';
import clsx from 'clsx';

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'subtle' | 'default' | 'prominent';
  interactive?: boolean;
  className?: string;
}

/**
 * Reusable GlassCard component implementing Apple VisionOS glassmorphism aesthetics.
 */
export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  variant = 'default',
  interactive = false,
  className,
  ...props
}) => {
  const baseClasses = 'rounded-3xl border transition-all duration-300 relative overflow-hidden backdrop-blur-xl';

  const variantClasses = {
    subtle: 'bg-okj-surface/30 dark:bg-white/[0.03] border-white/10 dark:border-white/[0.06] shadow-sm',
    default: 'bg-okj-surface/50 dark:bg-white/[0.06] border-white/15 dark:border-white/[0.10] shadow-[0_8px_32px_rgba(0,0,0,0.25)]',
    prominent: 'bg-okj-card/70 dark:bg-white/[0.10] border-okj-gold/30 dark:border-okj-gold/40 shadow-[0_12px_48px_rgba(211,168,92,0.12)]',
  }[variant];

  const interactiveClasses = interactive
    ? 'hover:scale-[1.01] hover:border-okj-gold/50 hover:shadow-[0_12px_40px_rgba(211,168,92,0.2)] cursor-pointer active:scale-[0.99]'
    : '';

  return (
    <div className={clsx(baseClasses, variantClasses, interactiveClasses, className)} {...props}>
      {/* Subtle top light reflection highlight */}
      <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent pointer-events-none" />
      {children}
    </div>
  );
};
