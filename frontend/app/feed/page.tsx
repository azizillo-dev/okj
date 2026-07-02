'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useWindowVirtualizer } from '@tanstack/react-virtual';
import { Sparkles, Compass, TrendingUp, Flame } from 'lucide-react';
import { postsApi } from '@/lib/api/posts';
import { Post, PostType } from '@/lib/api/types';
import { PostCard, IntentTag, SkeletonCard } from '@/components/ui';

const FILTER_TAGS: { label: string; value: string }[] = [
  { label: 'Barchasi', value: '' },
  { label: 'Iqtiboslar', value: 'QUOTE' },
  { label: 'Taqrizlar', value: 'REVIEW' },
  { label: 'Ko\'rgazma', value: 'SHOWCASE' },
  { label: 'Almashish', value: 'EXCHANGE' },
  { label: 'Sovg\'a', value: 'GIFT' },
  { label: 'Sotuv', value: 'SELL' },
];

export default function FeedPage() {
  const [activeFilter, setActiveFilter] = useState<string>('');
  const listRef = useRef<HTMLDivElement | null>(null);

  // Fetch feed with React Query infinite pagination
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status,
  } = useInfiniteQuery({
    queryKey: ['feed', activeFilter],
    queryFn: async ({ pageParam = 1 }) => {
      // If API fails or in standalone demo mode without running backend, return mock feed fallback
      try {
        const res = await postsApi.getFeed({ page: pageParam, type: activeFilter || undefined });
        return res;
      } catch {
        return {
          count: 3,
          next: null,
          previous: null,
          results: [
            {
              id: '1',
              user: { id: 'u1', username: 'navoiy_fan', first_name: 'Alisher', last_name: 'Rustamov', okj_id: 'OKJ-10492', total_xp: 1250 },
              post_type: 'QUOTE' as PostType,
              content: 'Odamiylik deb bilg\'il odamni, Onikim yo\'qtur xalq g\'amidan g\'ami.',
              book: { id: 'b1', title: 'Xamsai Mutahayyirin', slug: 'xamsai-mutahayyirin', authors: [{ id: 'a1', name: 'Alisher Navoiy' }] },
              quote_page: 45,
              media: [],
              likes_count: 42,
              comments_count: 7,
              created_at: new Date().toISOString(),
            },
            {
              id: '2',
              user: { id: 'u2', username: 'bookworm_uz', first_name: 'Malika', last_name: 'Saidova', okj_id: 'OKJ-20511', total_xp: 800 },
              post_type: 'EXCHANGE' as PostType,
              title: 'O\'tkan kunlar (Klassik nashr) almashamiz',
              content: 'Juda toza o\'qilgan kitob. o\'rniga Stiven King yoki Rey Bredberi asarlaridan biriga almashish niyatim bor.',
              price: 35000,
              book: { id: 'b2', title: 'O\'tkan kunlar', slug: 'otkan-kunlar', authors: [{ id: 'a2', name: 'Abdulla Qodiriy' }] },
              media: [],
              likes_count: 19,
              comments_count: 12,
              created_at: new Date().toISOString(),
            },
            {
              id: '3',
              user: { id: 'u3', username: 'intellect_99', first_name: 'Sardor', last_name: 'Ismoilov', okj_id: 'OKJ-31005', total_xp: 2100 },
              post_type: 'REVIEW' as PostType,
              title: 'Yulduzli tunlar — Tarixiy haqiqat fojiasi',
              content: 'Bobur mirzoning hayot yo\'lini chuqur tahlil qilgan eng kuchli o\'zbek romanlaridan biri. Har bir kitobxon o\'qishi shart deb hisoblayman.',
              book: { id: 'b3', title: 'Yulduzli tunlar', slug: 'yulduzli-tunlar', authors: [{ id: 'a3', name: 'Pirimqul Qodirov' }] },
              media: [],
              likes_count: 85,
              comments_count: 24,
              created_at: new Date().toISOString(),
            },
          ] as Post[],
        };
      }
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => {
      return lastPage?.next ? allPages.length + 1 : undefined;
    },
  });

  const allPosts = data?.pages.flatMap((p) => p.results) || [];

  // TanStack Window Virtualizer setup for DOM optimization
  const virtualizer = useWindowVirtualizer({
    count: hasNextPage ? allPosts.length + 1 : allPosts.length,
    estimateSize: () => 280, // Approximate height of PostCard
    overscan: 5,
    scrollMargin: listRef.current?.offsetTop || 0,
  });

  // Automatically fetch next page when virtual scroll reaches the end
  useEffect(() => {
    const [lastItem] = [...virtualizer.getVirtualItems()].reverse();
    if (!lastItem) return;

    if (
      lastItem.index >= allPosts.length - 1 &&
      hasNextPage &&
      !isFetchingNextPage
    ) {
      fetchNextPage();
    }
  }, [hasNextPage, fetchNextPage, allPosts.length, isFetchingNextPage, virtualizer.getVirtualItems()]);

  return (
    <div className="max-w-6xl mx-auto px-4 pt-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Main Feed Column (Spans 3 cols on desktop) */}
      <div className="lg:col-span-3 space-y-6">
        {/* Feed Header & Filter Tags */}
        <div className="space-y-4 bg-okj-surface/40 p-4 rounded-2xl border border-okj-card-border/60">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-okj-gold" />
              <h1 className="font-display font-bold text-lg text-okj-text-primary">Jonli Lenta</h1>
            </div>
            <span className="text-xs text-okj-text-muted">{allPosts.length} ta post ko&apos;rsatilmoqda</span>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
            {FILTER_TAGS.map((tag) => (
              <IntentTag
                key={tag.value}
                type={tag.label}
                active={activeFilter === tag.value}
                onClick={() => setActiveFilter(tag.value)}
              />
            ))}
          </div>
        </div>

        {/* Loading Skeleton state */}
        {status === 'pending' ? (
          <div className="space-y-4">
            <SkeletonCard variant="post" />
            <SkeletonCard variant="post" />
            <SkeletonCard variant="post" />
          </div>
        ) : (
          /* Virtualized Feed List */
          <div ref={listRef} className="relative w-full" style={{ height: `${virtualizer.getTotalSize()}px` }}>
            {virtualizer.getVirtualItems().map((virtualRow) => {
              const isLoaderRow = virtualRow.index > allPosts.length - 1;
              const post = allPosts[virtualRow.index];

              return (
                <div
                  key={virtualRow.index}
                  ref={virtualizer.measureElement}
                  data-index={virtualRow.index}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    transform: `translateY(${virtualRow.start - (virtualizer.options.scrollMargin || 0)}px)`,
                  }}
                  className="pb-4"
                >
                  {isLoaderRow ? (
                    hasNextPage ? (
                      <SkeletonCard variant="post" />
                    ) : (
                      <div className="p-4 text-center text-xs text-okj-text-muted">Lenta tugadi.</div>
                    )
                  ) : post ? (
                    <PostCard post={post} />
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Desktop Right Sidebar (Phase 2 Requirement 6) */}
      <aside className="hidden lg:block space-y-6">
        {/* Streak & Challenge Widget */}
        <div className="p-5 rounded-2xl bg-okj-card border border-okj-card-border space-y-4">
          <div className="flex items-center gap-2 text-okj-gold font-display font-bold text-sm">
            <Flame className="w-4 h-4 fill-okj-gold" />
            <span>Kundalik O&apos;qish Seriyasi</span>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="font-display font-black text-3xl text-okj-text-primary">12 Kun</div>
              <p className="text-xs text-okj-text-secondary">Faol kitobxonlik</p>
            </div>
            <div className="w-12 h-12 rounded-full bg-okj-gold/15 border border-okj-gold flex items-center justify-center font-bold text-okj-gold text-lg">
              🔥
            </div>
          </div>
        </div>

        {/* Trending Books Widget */}
        <div className="p-5 rounded-2xl bg-okj-card border border-okj-card-border space-y-4">
          <div className="flex items-center gap-2 font-display font-bold text-sm text-okj-text-primary">
            <TrendingUp className="w-4 h-4 text-okj-gold" />
            <span>Haftaning Top Kitoblari</span>
          </div>
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2 rounded-xl bg-okj-surface/60">
              <span className="font-bold text-okj-text-primary truncate">1. Yulduzli tunlar</span>
              <span className="text-okj-gold font-mono">4.9 ★</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-xl bg-okj-surface/60">
              <span className="font-bold text-okj-text-primary truncate">2. O&apos;tkan kunlar</span>
              <span className="text-okj-gold font-mono">4.8 ★</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-xl bg-okj-surface/60">
              <span className="font-bold text-okj-text-primary truncate">3. Alkimyogar</span>
              <span className="text-okj-gold font-mono">4.7 ★</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
