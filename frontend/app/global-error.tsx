'use client';

import React from 'react';
import { GlassErrorState } from '@/components/ui/glass/GlassErrorState';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="uz">
      <body className="bg-[#17233D] text-[#F3EDE0] font-sans antialiased min-h-screen flex items-center justify-center">
        <GlassErrorState
          variant="500"
          title="Halokatli Xatolik (Root Fatal Error)"
          description="Dastur poydevorida kutilmagan xato yuz berdi. Iltimos sahifani yangilang."
          error={error}
          onRetry={() => reset()}
          showHomeButton={true}
        />
      </body>
    </html>
  );
}
