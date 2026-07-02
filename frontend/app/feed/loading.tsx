import React from 'react';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { GlassSkeleton } from '@/components/ui/glass/GlassSkeleton';

export default function FeedLoading() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
      {/* Top stories/carousel skeleton */}
      <div className="flex gap-4 overflow-hidden pb-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex flex-col items-center gap-2 shrink-0">
            <GlassSkeleton variant="circular" width={64} height={64} className="border-2 border-okj-gold/40" />
            <GlassSkeleton variant="text" className="w-12 h-2.5" />
          </div>
        ))}
      </div>

      {/* Filter tabs skeleton */}
      <div className="flex gap-2 pb-2">
        <GlassSkeleton variant="rounded" className="w-24 h-9 rounded-full" />
        <GlassSkeleton variant="rounded" className="w-24 h-9 rounded-full" />
        <GlassSkeleton variant="rounded" className="w-24 h-9 rounded-full" />
      </div>

      {/* Feed Posts Skeleton List */}
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <SkeletonCard key={i} variant="post" />
        ))}
      </div>
    </div>
  );
}
