'use client';

import React from 'react';
import { GlassErrorState } from '@/components/ui/glass/GlassErrorState';

export default function PostDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <GlassErrorState
        variant="500"
        title="Post ma'lumotlarini yuklashda xato"
        description="Ushbu post yuklanmadi yoki unga kirish cheklangan."
        error={error}
        onRetry={() => reset()}
      />
    </div>
  );
}
