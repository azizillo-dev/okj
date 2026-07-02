import React from 'react';
import { SkeletonCard } from '@/components/ui/SkeletonCard';

export default function NotificationsLoading() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-4">
      <div className="h-8 w-40 rounded-xl bg-okj-surface/50 animate-pulse mb-6" />
      {Array.from({ length: 6 }).map((_, i) => (
        <SkeletonCard key={i} variant="notification" />
      ))}
    </div>
  );
}
