'use client';

import React from 'react';

interface GlassSkeletonProps {
  className?: string;
  variant?: 'rectangular' | 'circular' | 'rounded' | 'text';
  width?: string | number;
  height?: string | number;
}

/**
 * Enterprise-grade Glass Shimmer Skeleton primitive.
 * Produces smooth Apple VisionOS glassmorphism sweep animations with zero layout shifts.
 */
export const GlassSkeleton: React.FC<GlassSkeletonProps> = ({
  className = '',
  variant = 'rounded',
  width,
  height,
}) => {
  const shapeClasses = {
    rectangular: 'rounded-none',
    circular: 'rounded-full',
    rounded: 'rounded-2xl',
    text: 'rounded-md h-4 w-3/4',
  }[variant];

  return (
    <div
      className={`relative overflow-hidden bg-white/[0.04] border border-white/[0.08] backdrop-blur-md shrink-0 ${shapeClasses} ${className}`}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
      }}
      role="status"
      aria-label="Yuklanmoqda..."
    >
      {/* Moving glass shimmer highlight sweep */}
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/[0.12] to-transparent pointer-events-none" />
    </div>
  );
};
