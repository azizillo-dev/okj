'use client';

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export const QueryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 2 * 60 * 1000, // 2 minutes optimal freshness
            gcTime: 30 * 60 * 1000,   // 30 minutes garbage collection time
            refetchOnWindowFocus: true, // Focus refetch enabled for live updates
            refetchOnReconnect: true,   // Offline queue auto recovery
            retry: (failureCount, error: unknown) => {
              const status = (error as { code?: string })?.code;
              if (status?.includes('HTTP_404') || status?.includes('HTTP_401') || status?.includes('HTTP_403')) {
                return false;
              }
              return failureCount < 2;
            },
          },
          mutations: {
            retry: 0,
          },
        },
      })
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
};
