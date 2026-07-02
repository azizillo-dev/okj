'use client';

import React from 'react';
import Image from 'next/image';
import clsx from 'clsx';
import { BookOpen, Star } from 'lucide-react';
import { Book } from '@/lib/api/types';

export interface BookCover3DProps {
  book: Book;
  onClick?: () => void;
  className?: string;
}

/**
 * High-performance 3D Book Cover component using pure CSS 3D transforms.
 * Features realistic book spine, page edge shadow, and interactive tilt on hover.
 */
export const BookCover3D: React.FC<BookCover3DProps> = ({ book, onClick, className }) => {
  const authorNames = book.authors?.map((a) => a.name).join(', ') || 'Noma\'lum muallif';

  return (
    <div
      onClick={onClick}
      className={clsx('group relative inline-block cursor-pointer select-none p-4', className)}
      style={{ perspective: '1200px' }}
      role="button"
      tabIndex={0}
      aria-label={`${book.title} kitobini ko'rish`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
    >
      {/* 3D Rotating Container */}
      <div
        className="relative w-40 sm:w-48 aspect-[2/3] transition-transform duration-500 ease-out group-hover:[transform:rotateY(-18deg)_rotateX(6deg)_scale(1.04)] [transform-style:preserve-3d]"
      >
        {/* Desk drop shadow */}
        <div
          className="absolute -bottom-4 inset-x-2 h-4 rounded-full bg-black/50 blur-md transition-all duration-500 group-hover:-bottom-6 group-hover:scale-95 group-hover:bg-okj-gold/20"
          style={{ transform: 'rotateX(80deg)' }}
        />

        {/* Left Spine Thickness (Book Pages Edge) */}
        <div
          className="absolute top-0 left-0 w-6 h-full bg-gradient-to-r from-amber-100 via-[#EDE4D3] to-[#D5CBB9] border-l border-[#B3A894] rounded-l-sm shadow-inner"
          style={{
            transform: 'rotateY(-90deg) translateZ(12px)',
            transformOrigin: 'left',
          }}
        >
          {/* Page lines texture */}
          <div className="w-full h-full opacity-30 bg-[linear-gradient(to_bottom,transparent_2px,rgba(0,0,0,0.15)_2px)] bg-[size:100%_4px]" />
        </div>

        {/* Front Cover Face */}
        <div
          className="absolute inset-0 rounded-r-md rounded-l-sm overflow-hidden bg-okj-surface border border-white/20 shadow-2xl transition-shadow duration-500 group-hover:shadow-[12px_16px_40px_rgba(0,0,0,0.6)]"
          style={{ transform: 'translateZ(12px)' }}
        >
          {book.cover_image ? (
            <Image
              src={book.cover_image}
              alt={book.title}
              fill
              className="object-cover"
              sizes="(max-width: 640px) 160px, 192px"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center p-4 text-center bg-gradient-to-br from-okj-surface to-okj-bg-deep text-okj-text-primary">
              <BookOpen className="w-10 h-10 mb-2 text-okj-gold stroke-[1.5]" />
              <h4 className="font-display font-bold text-xs leading-tight line-clamp-3 mb-1">{book.title}</h4>
              <p className="text-[10px] text-okj-text-secondary line-clamp-1">{authorNames}</p>
            </div>
          )}

          {/* Book cover gloss sheen overlay */}
          <div className="absolute inset-0 bg-gradient-to-tr from-black/20 via-transparent to-white/15 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
        </div>
      </div>

      {/* Book Metadata below cover */}
      <div className="mt-5 text-center max-w-[192px]">
        <h4 className="font-display font-bold text-sm text-okj-text-primary group-hover:text-okj-gold transition-colors truncate">
          {book.title}
        </h4>
        <p className="text-xs text-okj-text-secondary truncate mt-0.5">{authorNames}</p>
        {book.average_rating !== undefined && (
          <div className="flex items-center justify-center gap-1 mt-1 text-xs text-okj-gold font-bold">
            <Star className="w-3.5 h-3.5 fill-okj-gold" />
            <span>{book.average_rating.toFixed(1)}</span>
          </div>
        )}
      </div>
    </div>
  );
};
