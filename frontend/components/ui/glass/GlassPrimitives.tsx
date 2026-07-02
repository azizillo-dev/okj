'use client';

import React from 'react';
import clsx from 'clsx';

export interface GlassBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'gold' | 'default' | 'success' | 'danger';
  children: React.ReactNode;
}

export const GlassBadge: React.FC<GlassBadgeProps> = ({
  variant = 'default',
  className,
  children,
  ...props
}) => {
  const variantClasses = {
    default: 'bg-white/10 text-okj-text-primary border-white/20',
    gold: 'bg-okj-gold/15 text-okj-gold border-okj-gold/30 shadow-sm shadow-okj-gold/10 font-bold',
    success: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    danger: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
  }[variant];

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-display border backdrop-blur-md select-none',
        variantClasses,
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

export interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
}

export const GlassInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, icon, ...props }, ref) => {
    return (
      <div className="relative flex items-center w-full">
        {icon && <span className="absolute left-3.5 text-okj-text-muted pointer-events-none">{icon}</span>}
        <input
          ref={ref}
          className={clsx(
            'w-full rounded-2xl bg-okj-surface/60 dark:bg-[#1A253D]/60 backdrop-blur-xl border border-white/15 px-4 py-2.5 text-xs text-okj-text-primary placeholder:text-okj-text-muted focus:outline-none focus:border-okj-gold/60 focus:ring-1 focus:ring-okj-gold/30 transition-all duration-200',
            icon && 'pl-10',
            className
          )}
          {...props}
        />
      </div>
    );
  }
);
GlassInput.displayName = 'GlassInput';

export interface GlassChipProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
  children: React.ReactNode;
}

export const GlassChip: React.FC<GlassChipProps> = ({ active = false, className, children, ...props }) => {
  return (
    <button
      type="button"
      className={clsx(
        'inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all duration-200 active:scale-95 select-none border backdrop-blur-md',
        active
          ? 'bg-okj-gold text-okj-bg-deep border-okj-gold font-bold shadow-md shadow-okj-gold/20'
          : 'bg-white/5 text-okj-text-secondary border-white/10 hover:bg-white/10 hover:text-okj-text-primary',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};

export interface GlassProgressProps {
  value: number; // 0 to 100
  className?: string;
}

export const GlassProgress: React.FC<GlassProgressProps> = ({ value, className }) => {
  const clamped = Math.min(Math.max(value, 0), 100);
  return (
    <div
      className={clsx('w-full h-2 rounded-full bg-white/10 overflow-hidden backdrop-blur-md border border-white/5', className)}
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className="h-full bg-gradient-to-r from-amber-400 to-okj-gold rounded-full transition-all duration-500 ease-out shadow-sm shadow-okj-gold/50"
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
};
