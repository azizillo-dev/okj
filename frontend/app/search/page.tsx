'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, BookOpen, Users, Compass, Loader2 } from 'lucide-react';
import { searchApi } from '@/lib/api/search';
import { BookCard, PostCard, Avatar, FollowButton, SkeletonCard } from '@/components/ui';

export default function SearchPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedTerm, setDebouncedTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'books' | 'users' | 'posts'>('all');

  // Debounce search term by 300ms (Requirement 3)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedTerm(searchTerm.trim());
    }, 300);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['search', debouncedTerm, activeTab],
    queryFn: async () => {
      if (!debouncedTerm) return null;
      return await searchApi.globalSearch(debouncedTerm, activeTab !== 'all' ? activeTab : undefined);
    },
    enabled: Boolean(debouncedTerm),
  });

  const tabs = [
    { id: 'all', label: 'Barchasi', icon: Search },
    { id: 'books', label: 'Kitoblar', icon: BookOpen },
    { id: 'users', label: 'Kitobxonlar', icon: Users },
    { id: 'posts', label: 'Postlar', icon: Compass },
  ] as const;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      {/* Search Input Bar */}
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-okj-text-muted" />
          <input
            type="text"
            placeholder="Kitob nomi, muallif, kitobxon ID (yoki kalit so'z) orqali qidiruv..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-10 py-4 rounded-2xl bg-okj-card border-2 border-okj-card-border text-base text-okj-text-primary placeholder:text-okj-text-muted focus:outline-none focus:border-okj-gold shadow-lg transition-colors"
          />
          {isLoading && (
            <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 animate-spin text-okj-gold" />
          )}
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-display font-bold transition-colors shrink-0 ${
                  isActive
                    ? 'bg-okj-gold text-okj-bg-deep shadow-md'
                    : 'bg-okj-surface text-okj-text-secondary hover:text-okj-text-primary hover:bg-okj-card border border-okj-card-border'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Results Area */}
      {!debouncedTerm ? (
        <div className="p-12 text-center rounded-3xl bg-okj-card/50 border border-dashed border-okj-card-border text-okj-text-secondary">
          <Search className="w-12 h-12 mx-auto mb-3 text-okj-text-muted stroke-[1.5]" />
          <p className="text-sm">Qidiruvni boshlash uchun yuqoridagi maydonga so&apos;z yozing.</p>
        </div>
      ) : isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SkeletonCard variant="book" />
          <SkeletonCard variant="book" />
        </div>
      ) : isError ? (
        <div className="p-8 text-center rounded-2xl bg-rose-500/10 text-rose-300 text-sm">
          Qidiruvda xatolik yuz berdi. Qaytadan urinib ko&apos;ring.
        </div>
      ) : data ? (
        <div className="space-y-8">
          {/* Books Result */}
          {(activeTab === 'all' || activeTab === 'books') && data.books && data.books.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-display font-bold text-sm uppercase tracking-wider text-okj-gold">
                Kitoblar ({data.books.length})
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {data.books.map((book: any) => (
                  <BookCard key={book.id} book={book} variant="compact" />
                ))}
              </div>
            </div>
          )}

          {/* Users Result */}
          {(activeTab === 'all' || activeTab === 'users') && data.users && data.users.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-display font-bold text-sm uppercase tracking-wider text-okj-gold">
                Kitobxonlar ({data.users.length})
              </h3>
              <div className="space-y-2">
                {data.users.map((user: any) => (
                  <div
                    key={user.id}
                    className="flex items-center justify-between p-3.5 rounded-2xl bg-okj-card border border-okj-card-border"
                  >
                    <div className="flex items-center gap-3">
                      <Avatar user={user} size="md" />
                      <div>
                        <h4 className="font-display font-bold text-sm text-okj-text-primary">
                          {user.first_name} {user.last_name || user.username}
                        </h4>
                        <p className="text-xs text-okj-text-secondary">{user.okj_id || user.username}</p>
                      </div>
                    </div>
                    <FollowButton userId={user.id} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Posts Result */}
          {(activeTab === 'all' || activeTab === 'posts') && data.posts && data.posts.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-display font-bold text-sm uppercase tracking-wider text-okj-gold">
                Postlar ({data.posts.length})
              </h3>
              <div className="space-y-4">
                {data.posts.map((post: any) => (
                  <PostCard key={post.id} post={post} />
                ))}
              </div>
            </div>
          )}

          {(!data.books || data.books.length === 0) &&
            (!data.users || data.users.length === 0) &&
            (!data.posts || data.posts.length === 0) && (
              <div className="p-8 text-center text-okj-text-secondary">
                &quot;{debouncedTerm}&quot; bo&apos;yicha hech qanday natija topilmadi.
              </div>
            )}
        </div>
      ) : null}
    </div>
  );
}
