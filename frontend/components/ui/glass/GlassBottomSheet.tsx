'use client';

import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import clsx from 'clsx';

export interface GlassBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

/**
 * Mobile-friendly GlassBottomSheet component with slide-up animation.
 */
export const GlassBottomSheet: React.FC<GlassBottomSheetProps> = ({
  isOpen,
  onClose,
  title,
  children,
  className,
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
    >
      <div
        className={clsx(
          'w-full max-w-lg rounded-t-3xl bg-okj-surface/95 dark:bg-[#1A253D]/95 backdrop-blur-2xl border-t border-x border-white/15 shadow-[0_-12px_40px_rgba(0,0,0,0.5)] p-6 max-h-[85vh] overflow-y-auto relative animate-in slide-in-from-bottom duration-300',
          className
        )}
      >
        {/* Grab handle indicator */}
        <div className="w-12 h-1.5 rounded-full bg-white/20 mx-auto mb-4" />

        <div className="flex items-center justify-between pb-3 mb-4 border-b border-white/10">
          <h3 className="font-display font-bold text-lg text-okj-text-primary">{title}</h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-okj-text-secondary hover:text-okj-text-primary hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div>{children}</div>
      </div>
    </div>
  );
};
