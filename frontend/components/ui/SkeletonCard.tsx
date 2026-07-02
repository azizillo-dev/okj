'use client';

import React from 'react';
import clsx from 'clsx';
import { GlassSkeleton } from '@/components/ui/glass/GlassSkeleton';

export type SkeletonVariant =
  | 'post'
  | 'book'
  | 'profile'
  | 'post-detail'
  | 'book-detail'
  | 'library'
  | 'marketplace'
  | 'comment'
  | 'search'
  | 'passport'
  | 'notification'
  | 'avatar';

interface SkeletonCardProps {
  variant?: SkeletonVariant;
  className?: string;
}

/**
 * Enterprise Professional Shimmer Glass Skeleton System.
 * Replaces all spinning animations with exact geometric silhouettes matching target components.
 * Prevents Cumulative Layout Shift (CLS) on every screen of OKJ platform.
 */
export const SkeletonCard: React.FC<SkeletonCardProps> = ({ variant = 'post', className }) => {
  if (variant === 'avatar') {
    return <GlassSkeleton variant="circular" width={44} height={44} className={className} />;
  }

  if (variant === 'comment') {
    return (
      <div className={clsx('flex items-start gap-3 p-3.5 rounded-2xl bg-okj-surface/30 border border-okj-card-border/30', className)}>
        <GlassSkeleton variant="circular" width={36} height={36} />
        <div className="flex-1 space-y-2">
          <div className="flex justify-between">
            <GlassSkeleton variant="text" className="w-24 h-3" />
            <GlassSkeleton variant="text" className="w-12 h-3" />
          </div>
          <GlassSkeleton variant="text" className="w-full h-3.5" />
          <GlassSkeleton variant="text" className="w-2/3 h-3.5" />
        </div>
      </div>
    );
  }

  if (variant === 'notification') {
    return (
      <div className={clsx('flex items-center gap-3.5 p-4 rounded-2xl bg-okj-surface/30 border border-okj-card-border/30', className)}>
        <GlassSkeleton variant="circular" width={44} height={44} />
        <div className="flex-1 space-y-2">
          <GlassSkeleton variant="text" className="w-5/6 h-3.5" />
          <GlassSkeleton variant="text" className="w-1/3 h-3" />
        </div>
        <GlassSkeleton variant="rounded" width={8} height={8} className="rounded-full" />
      </div>
    );
  }

  if (variant === 'book') {
    return (
      <div className={clsx('flex flex-col rounded-2xl bg-okj-card/60 border border-okj-card-border/40 overflow-hidden h-[280px]', className)}>
        <GlassSkeleton variant="rectangular" className="w-full aspect-[2/3]" />
        <div className="p-4 flex flex-col flex-1 gap-2.5">
          <GlassSkeleton variant="text" className="w-3/4 h-4" />
          <GlassSkeleton variant="text" className="w-1/2 h-3" />
          <div className="mt-auto pt-2 flex justify-between items-center border-t border-white/5">
            <GlassSkeleton variant="text" className="w-10 h-3" />
            <GlassSkeleton variant="text" className="w-14 h-3" />
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'book-detail') {
    return (
      <div className={clsx('max-w-4xl mx-auto p-4 md:p-8 space-y-8', className)}>
        <div className="flex flex-col md:flex-row gap-8 items-start">
          <GlassSkeleton variant="rounded" className="w-48 sm:w-64 aspect-[2/3] shrink-0 mx-auto md:mx-0 shadow-2xl" />
          <div className="flex-1 space-y-4 w-full">
            <GlassSkeleton variant="text" className="w-1/4 h-4" />
            <GlassSkeleton variant="text" className="w-3/4 h-8" />
            <GlassSkeleton variant="text" className="w-1/2 h-5" />
            <div className="flex gap-4 pt-2">
              <GlassSkeleton variant="rounded" className="w-28 h-10" />
              <GlassSkeleton variant="rounded" className="w-28 h-10" />
            </div>
            <div className="space-y-2 pt-4">
              <GlassSkeleton variant="text" className="w-full h-4" />
              <GlassSkeleton variant="text" className="w-full h-4" />
              <GlassSkeleton variant="text" className="w-4/5 h-4" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'profile') {
    return (
      <div className={clsx('p-6 md:p-8 rounded-3xl bg-okj-card/60 border border-okj-card-border/40 flex flex-col items-center gap-4 text-center', className)}>
        <GlassSkeleton variant="circular" width={96} height={96} />
        <GlassSkeleton variant="text" className="w-48 h-6" />
        <GlassSkeleton variant="text" className="w-32 h-4" />
        <div className="grid grid-cols-3 gap-4 w-full max-w-sm pt-4">
          <GlassSkeleton variant="rounded" className="h-16" />
          <GlassSkeleton variant="rounded" className="h-16" />
          <GlassSkeleton variant="rounded" className="h-16" />
        </div>
      </div>
    );
  }

  if (variant === 'passport') {
    return (
      <div className={clsx('p-6 rounded-3xl bg-okj-card/70 border border-okj-gold/30 space-y-6', className)}>
        <div className="flex justify-between items-center">
          <GlassSkeleton variant="text" className="w-40 h-6" />
          <GlassSkeleton variant="rounded" className="w-24 h-8" />
        </div>
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <GlassSkeleton key={i} variant="circular" width={80} height={80} className="mx-auto" />
          ))}
        </div>
      </div>
    );
  }

  if (variant === 'library' || variant === 'search' || variant === 'marketplace') {
    return (
      <div className={clsx('grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4', className)}>
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} variant="book" />
        ))}
      </div>
    );
  }

  if (variant === 'post-detail') {
    return (
      <div className={clsx('max-w-3xl mx-auto space-y-6 p-4', className)}>
        <SkeletonCard variant="post" />
        <div className="space-y-3 pt-4">
          <GlassSkeleton variant="text" className="w-32 h-5" />
          <SkeletonCard variant="comment" />
          <SkeletonCard variant="comment" />
        </div>
      </div>
    );
  }

  // Default: 'post' variant for Feed
  return (
    <div className={clsx('rounded-2xl bg-okj-card/60 border border-okj-card-border/40 p-5 space-y-4 min-h-[220px] flex flex-col justify-between', className)}>
      <div className="flex items-center gap-3">
        <GlassSkeleton variant="circular" width={44} height={44} />
        <div className="flex-1 space-y-2">
          <GlassSkeleton variant="text" className="w-1/3 h-4" />
          <GlassSkeleton variant="text" className="w-1/4 h-3" />
        </div>
        <GlassSkeleton variant="rounded" className="w-20 h-6 rounded-full" />
      </div>

      <div className="space-y-2.5 py-2">
        <GlassSkeleton variant="text" className="w-full h-4" />
        <GlassSkeleton variant="text" className="w-5/6 h-4" />
        <GlassSkeleton variant="text" className="w-2/3 h-4" />
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-white/5">
        <div className="flex gap-4">
          <GlassSkeleton variant="rounded" className="w-16 h-7 rounded-full" />
          <GlassSkeleton variant="rounded" className="w-20 h-7 rounded-full" />
        </div>
        <GlassSkeleton variant="circular" width={32} height={32} />
      </div>
    </div>
  );
};
