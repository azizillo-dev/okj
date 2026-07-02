import React from 'react';
import { SkeletonCard } from '@/components/ui/SkeletonCard';

export default function UserProfileLoading() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <SkeletonCard variant="profile" />
      <SkeletonCard variant="passport" />
    </div>
  );
}
