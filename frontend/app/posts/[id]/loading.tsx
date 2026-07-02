import React from 'react';
import { SkeletonCard } from '@/components/ui/SkeletonCard';

export default function PostDetailLoading() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <SkeletonCard variant="post-detail" />
    </div>
  );
}
