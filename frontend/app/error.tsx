'use client';

import React, { useEffect } from 'react';
import { GlassErrorState } from '@/components/ui/glass/GlassErrorState';

export default function GlobalRouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to reporting service
    console.error('OKJ Route Error Boundary caught:', error);
  }, [error]);

  return (
    <GlassErrorState
      variant="500"
      error={error}
      onRetry={() => reset()}
      showHomeButton={true}
    />
  );
}
