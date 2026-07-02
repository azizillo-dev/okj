import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Star, BookOpen, Share2, MessageCircle, ArrowLeft, BookmarkPlus } from 'lucide-react';
import { booksApi } from '@/lib/api/books';
import { Book } from '@/lib/api/types';

// Incremental Static Regeneration (ISR) configuration: revalidate every 1 hour (3600 seconds)
export const revalidate = 3600;

export default async function BookDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let book: Book | null = null;

  try {
    book = await booksApi.getBookBySlug(slug);
  } catch {
    book = null;
  }

  if (!book) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center">
        <div className="p-8 rounded-3xl bg-okj-card/80 border border-white/10 backdrop-blur-xl max-w-md mx-auto space-y-4 shadow-2xl">
          <BookOpen className="w-12 h-12 text-okj-gold mx-auto" />
          <h2 className="font-display font-bold text-xl text-okj-text-primary">Kitob topilmadi</h2>
          <p className="text-xs text-okj-text-secondary">
            Siz qidirayotgan kitob OKJ ma&apos;lumotlar bazasidan topilmadi yoki uning manzili o&apos;zgargan.
          </p>
          <Link
            href="/feed"
            className="inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-okj-gold text-okj-bg-deep font-display font-bold text-xs transition-transform active:scale-95 shadow-md"
          >
            Lentaga qaytish
          </Link>
        </div>
      </div>
    );
  }

  const authorNames = book.authors?.map((a) => a.name).join(', ') || 'Noma\'lum muallif';

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Back Navigation */}
      <Link
        href="/feed"
        className="inline-flex items-center gap-2 text-xs font-display font-bold text-okj-text-secondary hover:text-okj-gold transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Lentaga qaytish</span>
      </Link>

      {/* Book Main Card */}
      <div className="p-6 md:p-8 rounded-3xl bg-okj-card border border-okj-card-border grid grid-cols-1 md:grid-cols-3 gap-8 shadow-xl">
        {/* Left: Cover Image */}
        <div className="md:col-span-1 flex flex-col items-center">
          <div className="relative w-full max-w-[240px] aspect-[2/3] rounded-2xl overflow-hidden bg-okj-surface shadow-2xl border border-okj-card-border">
            {book.cover_image ? (
              <Image src={book.cover_image} alt={book.title} fill className="object-cover" priority sizes="(max-width: 768px) 80vw, 240px" />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center text-okj-text-muted">
                <BookOpen className="w-16 h-16 mb-2 stroke-[1.5]" />
                <span className="text-xs">{book.title}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right: Book Details */}
        <div className="md:col-span-2 flex flex-col justify-between space-y-6">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-display font-bold uppercase tracking-widest text-okj-gold">
              <span>OKJ Rasmiy Katalogi</span>
            </div>

            <h1 className="font-display font-black text-3xl md:text-4xl text-okj-text-primary leading-tight">
              {book.title}
            </h1>

            <p className="text-base text-okj-text-secondary font-medium">Muallif: <span className="text-okj-text-primary font-bold">{authorNames}</span></p>

            <div className="flex items-center gap-4 py-2">
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-okj-gold/15 text-okj-gold font-bold text-sm">
                <Star className="w-4 h-4 fill-okj-gold" />
                <span>{book.average_rating ? book.average_rating.toFixed(2) : '5.00'}</span>
              </div>
              {book.ratings_count && (
                <span className="text-xs text-okj-text-muted">{book.ratings_count} ta baho</span>
              )}
              {book.isbn_13 && (
                <span className="text-xs font-mono text-okj-text-secondary">ISBN: {book.isbn_13}</span>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <h3 className="font-display font-bold text-sm uppercase tracking-wider text-okj-text-secondary">Annotatsiya</h3>
            <p className="text-sm text-okj-text-primary leading-relaxed font-body">
              {book.description || 'Ushbu kitob haqida annotatsiya ma\'lumotlari to\'plamoqda.'}
            </p>
          </div>

          {/* Actions */}
          <div className="pt-4 border-t border-okj-card-border/60 flex flex-wrap items-center gap-3">
            <button className="flex items-center gap-2 px-6 py-3 rounded-xl bg-okj-gold text-okj-bg-deep font-display font-bold text-sm shadow-md hover:bg-okj-gold/90 transition-all active:scale-95">
              <BookmarkPlus className="w-4 h-4 stroke-[2.5]" />
              <span>O&apos;qimoqchiman</span>
            </button>
            <button className="flex items-center gap-2 px-5 py-3 rounded-xl bg-okj-surface text-okj-text-primary border border-okj-card-border hover:bg-okj-card text-sm font-medium transition-colors">
              <MessageCircle className="w-4 h-4" />
              <span>Taqriz yozish</span>
            </button>
            <button className="p-3 rounded-xl bg-okj-surface text-okj-text-secondary hover:text-okj-text-primary border border-okj-card-border transition-colors">
              <Share2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
