'use client';

import React from 'react';
import Link from 'next/link';
import { BookOpen, Sparkles, ChevronRight } from 'lucide-react';
import { Book, Post } from '@/lib/api/types';
import { GlassCard } from '@/components/ui/glass';
import { BookCover3D } from '@/components/ui/premium';

interface RelatedContentWidgetProps {
  currentBook?: Book | null;
  relatedPosts: Post[];
}

export const RelatedContentWidget: React.FC<RelatedContentWidgetProps> = ({ currentBook, relatedPosts }) => {
  // Sample fallback related books if no actual list passed
  const sampleBooks: Book[] = currentBook
    ? [
        currentBook,
        { id: 'rel-1', title: 'O\'tkan kunlar', slug: 'otkan-kunlar', authors: [{ id: 'a2', name: 'Abdulla Qodiriy' }] },
        { id: 'rel-2', title: 'Alkimyogar', slug: 'alkimyogar', authors: [{ id: 'a3', name: 'Paulo Koelyo' }] },
      ]
    : [
        { id: 'rel-1', title: 'O\'tkan kunlar', slug: 'otkan-kunlar', authors: [{ id: 'a2', name: 'Abdulla Qodiriy' }] },
        { id: 'rel-2', title: 'Alkimyogar', slug: 'alkimyogar', authors: [{ id: 'a3', name: 'Paulo Koelyo' }] },
      ];

  return (
    <div className="space-y-8 pt-4">
      {/* Related Books Carousel */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-2">
          <h3 className="font-display font-bold text-base text-okj-text-primary flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-okj-gold" />
            <span>Mavzuga O&apos;xshash Kitoblar</span>
          </h3>
          <Link href="/search" className="text-xs text-okj-gold hover:underline flex items-center gap-0.5">
            <span>Barchasi</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="flex items-center gap-8 overflow-x-auto pb-4 pt-2 no-scrollbar px-2 justify-start sm:justify-around">
          {sampleBooks.map((b) => (
            <div key={b.id} className="shrink-0 text-center">
              <BookCover3D book={b} />
            </div>
          ))}
        </div>
      </div>

      {/* Related Posts Showcase */}
      {relatedPosts && relatedPosts.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 border-b border-white/10 pb-2">
            <Sparkles className="w-4 h-4 text-okj-gold" />
            <h3 className="font-display font-bold text-base text-okj-text-primary">Shu Kitob Yuzasidan Boshqa Postlar</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {relatedPosts.map((rp) => (
              <Link key={rp.id} href={`/posts/${rp.id}`}>
                <GlassCard variant="subtle" className="p-4 hover:border-okj-gold/40 transition-all group space-y-2">
                  <div className="flex items-center justify-between text-xs text-okj-text-muted">
                    <span className="font-bold text-okj-text-primary group-hover:text-okj-gold">
                      {rp.user.first_name} {rp.user.last_name || rp.user.username}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-okj-gold/10 text-okj-gold font-mono text-[10px]">
                      {rp.post_type}
                    </span>
                  </div>
                  <p className="text-xs text-okj-text-secondary line-clamp-2 italic">&quot;{rp.content}&quot;</p>
                </GlassCard>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
