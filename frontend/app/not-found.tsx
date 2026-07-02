import React from 'react';
import { GlassErrorState } from '@/components/ui/glass/GlassErrorState';

export default function GlobalNotFound() {
  return (
    <GlassErrorState
      variant="404"
      showHomeButton={true}
    />
  );
}
