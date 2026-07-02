'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useInfiniteQuery, useQueryClient } from '@tanstack/react-query';
import { useWindowVirtualizer } from '@tanstack/react-virtual';
import { Compass, TrendingUp, Flame, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';
import { postsApi } from '@/lib/api/posts';
import { PostCard, IntentTag, SkeletonCard } from '@/components/ui';
import { GlassCard, GlassButton } from '@/components/ui/glass';

const FILTER_TAGS: { label: string; value: string }[] = [
  { label: 'Barchasi', value: '' },
  { label: 'Iqtiboslar', value: 'QUOTE' },
  { label: 'Taqrizlar', value: 'REVIEW' },
  { label: "Ko'rgazma", value: 'SHOWCASE' },
  { label: 'Almashish', value: 'EXCHANGE' },
  { label: "Sovg'a", value: 'GIFT' },
  { label: 'Sotuv', value: 'SELL' },
];

export default function FeedPage() {
  const [activeFilter, setActiveFilter] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const listRef = useRef<HTMLDivElement | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const queryClient = useQueryClient();

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status,
    isError,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['feed', activeFilter],
    queryFn: async ({ pageParam = 1 }) => {
      const res = await postsApi.getFeed({ page: pageParam, type: activeFilter || undefined });
      return res;
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => {
      return lastPage?.next ? allPages.length + 1 : undefined;
    },
  });

  const allPosts = data?.pages.flatMap((p) => p.results) || [];

  // Pull To Refresh handler
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await queryClient.invalidateQueries({ queryKey: ['feed'] });
    await refetch();
    setTimeout(() => setIsRefreshing(false), 500);
  }, [queryClient, refetch]);

  // Virtualized rendering
  const virtualizer = useWindowVirtualizer({
    count: hasNextPage ? allPosts.length + 1 : allPosts.length,
    estimateSize: () => 320,
    overscan: 5,
    scrollMargin: 0,
  });

  // Intersection Observer for robust bottom trigger
  useEffect(() => {
    if (!loadMoreRef.current || !hasNextPage || isFetchingNextPage) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { rootMargin: '400px' }
    );

    observer.observe(loadMoreRef.current);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <div className="max-w-6xl mx-auto px-4 pt-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Main Feed Column */}
      <div className="lg:col-span-3 space-y-6" role="feed" aria-label="Kitobxonlik lentasi">
        {/* Header & Pull To Refresh */}
        <GlassCard variant="subtle" className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Compass className="w-5 h-5 text-okj-gold" />
              <h1 className="font-display font-black text-xl text-okj-text-primary">Jonli Lenta</h1>
            </div>

            <button
              type="button"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 text-okj-text-secondary hover:text-okj-text-primary text-xs font-medium transition-all active:scale-95 disabled:opacity-50"
              aria-label="Lentani yangilash"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-okj-gold' : ''}`} />
              <span>{isRefreshing ? 'Yangilanmoqda...' : 'Yangilash'}</span>
            </button>
          </div>

          {/* Filter Tags */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar" role="tablist" aria-label="Lentani filtrlash">
            {FILTER_TAGS.map((tag) => (
              <IntentTag
                key={tag.value}
                type={tag.label}
                active={activeFilter === tag.value}
                onClick={() => setActiveFilter(tag.value)}
              />
            ))}
          </div>
        </GlassCard>

        {/* Error State */}
        {isError && (
          <GlassCard variant="default" className="p-8 text-center space-y-4">
            <AlertCircle className="w-12 h-12 text-rose-400 mx-auto" />
            <div className="space-y-1">
              <h3 className="font-display font-bold text-lg text-okj-text-primary">Lentani yuklashda xatolik yuz berdi</h3>
              <p className="text-xs text-okj-text-secondary max-w-sm mx-auto">
                Tarmoqda aloqa uzildi yoki serverda muammo yuzaga keldi. Iltimos qaytadan urinib ko&apos;ring.
              </p>
            </div>
            <GlassButton variant="primary" onClick={() => refetch()}>
              Qaytadan Urinish
            </GlassButton>
          </GlassCard>
        )}

        {/* Skeleton Loading State */}
        {status === 'pending' && (
          <div className="space-y-4" aria-busy="true" aria-label="Postlar yuklanmoqda">
            <SkeletonCard variant="post" />
            <SkeletonCard variant="post" />
            <SkeletonCard variant="post" />
          </div>
        )}

        {/* Empty State */}
        {status === 'success' && allPosts.length === 0 && (
          <GlassCard variant="default" className="p-12 text-center space-y-4">
            <Sparkles className="w-12 h-12 text-okj-gold mx-auto" />
            <div className="space-y-1">
              <h3 className="font-display font-bold text-lg text-okj-text-primary">Hozircha postlar mavjud emas</h3>
              <p className="text-xs text-okj-text-secondary max-w-sm mx-auto">
                Siz tanlagan filtr bo&apos;yicha hech kim post qoldirmagan. Birinchi bo&apos;lib fikringiz bilan bo\'lishing!
              </p>
            </div>
          </GlassCard>
        )}

        {/* Virtualized Feed Rendering */}
        {status === 'success' && allPosts.length > 0 && (
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
                  className="pb-6"
                >
                  {isLoaderRow ? (
                    <div ref={loadMoreRef} className="py-4">
                      {hasNextPage ? (
                        <SkeletonCard variant="post" />
                      ) : (
                        <div className="p-4 text-center text-xs text-okj-text-muted font-mono">
                          ✓ Barcha postlar ko&apos;rib chiqildi
                        </div>
                      )}
                    </div>
                  ) : post ? (
                    <PostCard post={post} />
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Desktop Right Sidebar Widgets */}
      <aside className="hidden lg:block space-y-6">
        <GlassCard variant="prominent" className="p-5 space-y-4">
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
        </GlassCard>

        <GlassCard variant="default" className="p-5 space-y-4">
          <div className="flex items-center gap-2 font-display font-bold text-sm text-okj-text-primary">
            <TrendingUp className="w-4 h-4 text-okj-gold" />
            <span>Haftaning Top Kitoblari</span>
          </div>
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-okj-surface/60 hover:bg-okj-surface transition-colors cursor-pointer">
              <span className="font-bold text-okj-text-primary truncate">1. Yulduzli tunlar</span>
              <span className="text-okj-gold font-mono">4.9 ★</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-okj-surface/60 hover:bg-okj-surface transition-colors cursor-pointer">
              <span className="font-bold text-okj-text-primary truncate">2. O&apos;tkan kunlar</span>
              <span className="text-okj-gold font-mono">4.8 ★</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-okj-surface/60 hover:bg-okj-surface transition-colors cursor-pointer">
              <span className="font-bold text-okj-text-primary truncate">3. Alkimyogar</span>
              <span className="text-okj-gold font-mono">4.7 ★</span>
            </div>
          </div>
        </GlassCard>
      </aside>
    </div>
  );
}
