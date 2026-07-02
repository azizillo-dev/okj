'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import clsx from 'clsx';
import { Star, BookOpen } from 'lucide-react';
import { Book } from '@/lib/api/types';

interface BookCardProps {
  book: Book;
  variant?: 'compact' | 'full';
}

export const BookCard: React.FC<BookCardProps> = ({ book, variant = 'full' }) => {
  const authorNames = book.authors?.map((a) => a.name).join(', ') || 'Noma\'lum muallif';

  if (variant === 'compact') {
    return (
      <Link
        href={`/books/${book.slug}`}
        className="group flex items-center gap-3 p-2 rounded-xl bg-okj-card hover:bg-okj-surface border border-okj-card-border transition-colors duration-200"
      >
        <div className="relative w-12 h-16 rounded-lg overflow-hidden shrink-0 bg-okj-surface shadow">
          {book.cover_image ? (
            <Image src={book.cover_image} alt={book.title} fill className="object-cover" sizes="48px" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-okj-text-muted">
              <BookOpen className="w-5 h-5" />
            </div>
          )}
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="font-display font-bold text-sm text-okj-text-primary group-hover:text-okj-gold truncate transition-colors">
            {book.title}
          </h4>
          <p className="text-xs text-okj-text-secondary truncate">{authorNames}</p>
          {book.average_rating !== undefined && (
            <div className="flex items-center gap-1 mt-1 text-xs text-okj-gold">
              <Star className="w-3 h-3 fill-okj-gold" />
              <span>{book.average_rating.toFixed(1)}</span>
            </div>
          )}
        </div>
      </Link>
    );
  }

  return (
    <Link
      href={`/books/${book.slug}`}
      className="group flex flex-col rounded-2xl bg-okj-card border border-okj-card-border overflow-hidden hover:border-okj-gold/50 transition-colors duration-300"
    >
      <div className="relative w-full aspect-[2/3] bg-okj-surface overflow-hidden">
        {book.cover_image ? (
          <Image
            src={book.cover_image}
            alt={book.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-500"
            sizes="(max-width: 768px) 50vw, 33vw"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center p-4 text-center text-okj-text-muted">
            <BookOpen className="w-12 h-12 mb-2 stroke-[1.5]" />
            <span className="text-xs">{book.title}</span>
          </div>
        )}
      </div>
      <div className="p-4 flex flex-col flex-1">
        <h3 className="font-display font-bold text-base text-okj-text-primary group-hover:text-okj-gold line-clamp-2 transition-colors mb-1">
          {book.title}
        </h3>
        <p className="text-xs text-okj-text-secondary line-clamp-1 mb-3">{authorNames}</p>
        <div className="mt-auto flex items-center justify-between text-xs text-okj-text-muted pt-2 border-t border-okj-card-border/50">
          <div className="flex items-center gap-1 text-okj-gold font-medium">
            <Star className="w-3.5 h-3.5 fill-okj-gold" />
            <span>{book.average_rating ? book.average_rating.toFixed(1) : '5.0'}</span>
          </div>
          {book.isbn_13 && <span className="font-mono text-[10px]">{book.isbn_13}</span>}
        </div>
      </div>
    </Link>
  );
};
