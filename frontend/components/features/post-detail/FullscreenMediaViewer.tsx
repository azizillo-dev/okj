'use client';

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ZoomIn, ZoomOut, ChevronLeft, ChevronRight, Download } from 'lucide-react';
import { PostMedia } from '@/lib/api/types';

interface FullscreenMediaViewerProps {
  media: PostMedia[];
  initialIndex: number;
  isOpen: boolean;
  onClose: () => void;
}

export const FullscreenMediaViewer: React.FC<FullscreenMediaViewerProps> = ({
  media,
  initialIndex,
  isOpen,
  onClose,
}) => {
  const [currentIndex, setCurrentIndex] = useState(initialIndex || 0);
  const [scale, setScale] = useState(1);

  const handlePrev = React.useCallback(() => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : media.length - 1));
    setScale(1);
  }, [media.length]);

  const handleNext = React.useCallback(() => {
    setCurrentIndex((prev) => (prev < media.length - 1 ? prev + 1 : 0));
    setScale(1);
  }, [media.length]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') handlePrev();
      if (e.key === 'ArrowRight') handleNext();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, handlePrev, handleNext, onClose]);

  if (!isOpen || !media || media.length === 0) return null;

  const currentMedia = media[currentIndex] || media[0];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-2xl p-4 select-none"
        onClick={onClose}
        role="dialog"
        aria-modal="true"
        aria-label="To'liq ekranda ko'rish modali"
      >
        {/* Top Controls Bar */}
        <div
          className="absolute top-4 inset-x-4 z-10 flex items-center justify-between p-3 rounded-2xl bg-white/10 border border-white/15 backdrop-blur-md text-white"
          onClick={(e) => e.stopPropagation()}
        >
          <span className="text-xs font-mono">
            {currentIndex + 1} / {media.length}
          </span>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setScale((prev) => Math.min(prev + 0.5, 3))}
              className="p-2 rounded-xl hover:bg-white/15 transition-colors"
              aria-label="Yaqinlashtirish"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setScale((prev) => Math.max(prev - 0.5, 1))}
              className="p-2 rounded-xl hover:bg-white/15 transition-colors"
              aria-label="Uzoqlashtirish"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <a
              href={currentMedia.file_url}
              download
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-xl hover:bg-white/15 transition-colors"
              aria-label="Yuklab olish"
            >
              <Download className="w-4 h-4" />
            </a>
            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-xl bg-rose-500/30 hover:bg-rose-500/50 text-rose-300 transition-colors ml-2"
              aria-label="Yopish"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Main Media View with Zoom */}
        <div
          className="relative w-full max-w-5xl h-[80vh] flex items-center justify-center overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <motion.div
            animate={{ scale }}
            transition={{ type: 'spring', damping: 25 }}
            className="relative w-full h-full flex items-center justify-center cursor-grab active:cursor-grabbing"
            onDoubleClick={() => setScale((prev) => (prev > 1 ? 1 : 2))}
          >
            {currentMedia.media_type === 'VIDEO' ? (
              <video
                src={currentMedia.file_url}
                controls
                autoPlay
                className="max-w-full max-h-full rounded-xl shadow-2xl"
              />
            ) : (
              <Image
                src={currentMedia.file_url}
                alt="Fullscreen view"
                fill
                className="object-contain"
                sizes="100vw"
                priority
              />
            )}
          </motion.div>
        </div>

        {/* Navigation Arrows */}
        {media.length > 1 && (
          <>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handlePrev();
              }}
              className="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-2xl bg-white/10 hover:bg-white/20 border border-white/15 text-white transition-all active:scale-95 z-10"
              aria-label="Oldingi rasm"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleNext();
              }}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-2xl bg-white/10 hover:bg-white/20 border border-white/15 text-white transition-all active:scale-95 z-10"
              aria-label="Keyingi rasm"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          </>
        )}
      </motion.div>
    </AnimatePresence>
  );
};
