import React from 'react';
import { SkeletonCard } from '@/components/ui/SkeletonCard';

export default function BookDetailLoading() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <SkeletonCard variant="book-detail" />
    </div>
  );
}
