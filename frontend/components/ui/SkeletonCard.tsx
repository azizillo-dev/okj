'use client';

import React from 'react';
import clsx from 'clsx';

interface SkeletonCardProps {
  variant?: 'post' | 'book' | 'profile';
  className?: string;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({ variant = 'post', className }) => {
  if (variant === 'book') {
    return (
      <div
        className={clsx(
          'flex flex-col rounded-2xl bg-okj-card border border-okj-card-border overflow-hidden animate-pulse h-[280px]',
          className
        )}
      >
        <div className="w-full aspect-[2/3] bg-okj-surface" />
        <div className="p-4 flex flex-col flex-1 gap-2">
          <div className="h-4 bg-okj-surface rounded w-3/4" />
          <div className="h-3 bg-okj-surface rounded w-1/2" />
          <div className="mt-auto h-3 bg-okj-surface rounded w-full" />
        </div>
      </div>
    );
  }

  if (variant === 'profile') {
    return (
      <div
        className={clsx(
          'p-6 rounded-3xl bg-okj-card border border-okj-card-border animate-pulse flex flex-col items-center gap-4 text-center',
          className
        )}
      >
        <div className="w-24 h-24 rounded-full bg-okj-surface" />
        <div className="w-48 h-6 bg-okj-surface rounded-md" />
        <div className="w-32 h-4 bg-okj-surface rounded-md" />
        <div className="w-full h-12 bg-okj-surface rounded-xl mt-2" />
      </div>
    );
  }

  // Default: 'post' variant matching exact feed item dimensions to prevent Cumulative Layout Shift (CLS)
  return (
    <div
      className={clsx(
        'rounded-2xl bg-okj-card border border-okj-card-border p-4 animate-pulse min-h-[220px] flex flex-col justify-between',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-11 h-11 rounded-full bg-okj-surface shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-okj-surface rounded w-1/3" />
          <div className="h-3 bg-okj-surface rounded w-1/4" />
        </div>
        <div className="w-16 h-6 bg-okj-surface rounded-full" />
      </div>

      {/* Content lines */}
      <div className="space-y-2.5 my-4">
        <div className="h-4 bg-okj-surface rounded w-5/6" />
        <div className="h-4 bg-okj-surface rounded w-full" />
        <div className="h-4 bg-okj-surface rounded w-3/4" />
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-okj-card-border/30">
        <div className="w-16 h-6 bg-okj-surface rounded-full" />
        <div className="w-12 h-6 bg-okj-surface rounded-full" />
      </div>
    </div>
  );
};
