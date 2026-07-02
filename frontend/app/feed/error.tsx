'use client';

import React from 'react';
import { GlassErrorState } from '@/components/ui/glass/GlassErrorState';

export default function FeedError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <GlassErrorState
        variant="network"
        title="Lentani Yuklab Bo'lmadi"
        description="Jonli postlar lentasi bilan aloqa o'rnatishda xatolik. Qaytadan urinib ko'ring."
        error={error}
        onRetry={() => reset()}
      />
    </div>
  );
}
