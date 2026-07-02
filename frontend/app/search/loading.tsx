import React from 'react';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { GlassSkeleton } from '@/components/ui/glass/GlassSkeleton';

export default function SearchLoading() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <GlassSkeleton variant="rounded" className="w-full h-14" />
      <div className="flex gap-2">
        <GlassSkeleton variant="rounded" className="w-20 h-8 rounded-full" />
        <GlassSkeleton variant="rounded" className="w-24 h-8 rounded-full" />
        <GlassSkeleton variant="rounded" className="w-24 h-8 rounded-full" />
      </div>
      <SkeletonCard variant="search" />
    </div>
  );
}
