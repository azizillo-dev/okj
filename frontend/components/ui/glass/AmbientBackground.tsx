'use client';

import React from 'react';

/**
 * Premium Apple VisionOS style ambient glowing background.
 * Uses pure CSS radial-gradient and blur for 60+ FPS performance without WebGL/Three.js overhead.
 */
export const AmbientBackground: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`fixed inset-0 pointer-events-none overflow-hidden z-0 ${className}`} aria-hidden="true">
      {/* Deep Indigo/Purple top-left aurora sphere */}
      <div
        className="absolute -top-32 -left-32 w-[500px] h-[500px] rounded-full opacity-30 dark:opacity-20 transition-opacity duration-1000 animate-pulse"
        style={{
          background: 'radial-gradient(circle, rgba(99, 102, 241, 0.45) 0%, rgba(23, 35, 61, 0) 70%)',
          filter: 'blur(90px)',
        }}
      />

      {/* Gold/Terracotta center-right accent glow */}
      <div
        className="absolute top-1/3 -right-40 w-[600px] h-[600px] rounded-full opacity-25 dark:opacity-15 transition-opacity duration-1000"
        style={{
          background: 'radial-gradient(circle, rgba(211, 168, 92, 0.4) 0%, rgba(193, 105, 74, 0.1) 50%, rgba(0, 0, 0, 0) 70%)',
          filter: 'blur(110px)',
        }}
      />

      {/* Subtle Cyan/Blue bottom aurora sphere */}
      <div
        className="absolute -bottom-40 left-1/4 w-[700px] h-[500px] rounded-full opacity-20 dark:opacity-15"
        style={{
          background: 'radial-gradient(circle, rgba(56, 189, 248, 0.3) 0%, rgba(27, 39, 64, 0) 70%)',
          filter: 'blur(120px)',
        }}
      />
    </div>
  );
};
