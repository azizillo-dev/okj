'use client';

import React, { useState } from 'react';
import { Layers, CheckCircle2 } from 'lucide-react';
import { Avatar, PassportStamp, BookCard, PostCard, FollowButton, IntentTag, SkeletonCard } from '@/components/ui';
import { Post, Book } from '@/lib/api/types';

export default function ComponentsPreviewPage() {
  const [activeTag, setActiveTag] = useState('Barchasi');

  const sampleUser = {
    id: 'u-demo',
    username: 'navoiy_fan',
    first_name: 'Alisher',
    last_name: 'Rustamov',
    okj_id: 'OKJ-10492',
    total_xp: 1450,
  };

  const sampleBook: Book = {
    id: 'b-demo',
    title: 'Xamsai Mutahayyirin',
    slug: 'xamsai-mutahayyirin',
    authors: [{ id: 'a1', name: 'Alisher Navoiy' }],
    average_rating: 4.95,
    isbn_13: '978-9943-00-111-1',
  };

  const sampleQuotePost: Post = {
    id: 'p-1',
    user: sampleUser,
    book: sampleBook,
    post_type: 'QUOTE',
    content: 'Odamiylik deb bilg\'il odamni, Onikim yo\'qtur xalq g\'amidan g\'ami.',
    quote_page: 45,
    media: [],
    likes_count: 142,
    comments_count: 18,
    created_at: new Date().toISOString(),
  };

  const sampleExchangePost: Post = {
    id: 'p-2',
    user: { ...sampleUser, username: 'bookworm_uz', first_name: 'Malika', okj_id: 'OKJ-20511' },
    book: { id: 'b2', title: 'O\'tkan kunlar', slug: 'otkan-kunlar', authors: [{ id: 'a2', name: 'Abdulla Qodiriy' }] },
    post_type: 'EXCHANGE',
    title: 'O\'tkan kunlar (Klassik muqovada) almashishga',
    content: 'Kitob bir marta ehtiyotkorona o\'qilgan. O\'rniga jahon adabiyotidan yoki falsafiy asarlardan birortasini almashtirmoqchiman.',
    price: 45000,
    media: [],
    likes_count: 38,
    comments_count: 9,
    created_at: new Date().toISOString(),
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-12">
      {/* Header */}
      <div className="p-6 md:p-8 rounded-3xl bg-okj-surface border border-okj-card-border space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-okj-gold/15 text-okj-gold text-xs font-display font-bold uppercase tracking-widest">
          <Layers className="w-3.5 h-3.5" />
          <span>Design Systems Showcase</span>
        </div>
        <h1 className="font-display font-black text-3xl md:text-4xl text-okj-text-primary">
          OKJ Design Token & UI Komponentlar Katalogi
        </h1>
        <p className="text-sm text-okj-text-secondary max-w-2xl font-body">
          Bu sahifada barcha 7 ta tasdiqlangan UI komponentlar (Storybook uslubida) interaktiv holatida namoyish etilgan.
        </p>
      </div>

      {/* 1. Avatar Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-okj-card-border pb-2">
          1. &lt;Avatar /&gt; Komponenti (sm | md | lg)
        </h2>
        <div className="p-6 rounded-2xl bg-okj-card border border-okj-card-border flex flex-wrap items-center gap-6">
          <div className="flex flex-col items-center gap-2">
            <Avatar user={sampleUser} size="sm" />
            <span className="text-xs text-okj-text-muted font-mono">sm (32px)</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Avatar user={sampleUser} size="md" />
            <span className="text-xs text-okj-text-muted font-mono">md (44px)</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Avatar user={sampleUser} size="lg" />
            <span className="text-xs text-okj-text-muted font-mono">lg (64px)</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Avatar user={{ id: 'hash-2', first_name: 'Ziyoda', last_name: 'Karimova' }} size="md" />
            <span className="text-xs text-okj-text-muted font-mono">Hash rang (Z.K)</span>
          </div>
        </div>
      </section>

      {/* 2. PassportStamp Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-okj-card-border pb-2">
          2. &lt;PassportStamp /&gt; Komponenti (Unlocked & Locked)
        </h2>
        <div className="p-6 rounded-2xl bg-okj-card border border-okj-card-border flex flex-wrap gap-6">
          <PassportStamp icon="🏛️" label="Tarix Bilag'oni" locked={false} />
          <PassportStamp icon="🔥" label="7 Kunlik Seriya" locked={false} />
          <PassportStamp icon="✍️" label="Iqtibos Ustasi" locked={false} />
          <PassportStamp icon="💎" label="Afsonaviy Daraja" locked={true} />
        </div>
      </section>

      {/* 3. BookCard Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-okj-card-border pb-2">
          3. &lt;BookCard /&gt; Komponenti (Compact & Full)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <span className="text-xs text-okj-text-muted font-mono">Compact variant:</span>
            <BookCard book={sampleBook} variant="compact" />
          </div>
          <div className="space-y-2 md:col-span-2 max-w-xs">
            <span className="text-xs text-okj-text-muted font-mono">Full variant:</span>
            <BookCard book={sampleBook} variant="full" />
          </div>
        </div>
      </section>

      {/* 4. PostCard Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-okj-card-border pb-2">
          4. &lt;PostCard /&gt; Komponenti (Quote vs Exchange/Sell variantlari)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <span className="text-xs text-okj-text-muted font-mono">Quote post (Parchment fon):</span>
            <PostCard post={sampleQuotePost} />
          </div>
          <div className="space-y-2">
            <span className="text-xs text-okj-text-muted font-mono">Exchange post (Terracotta urg&apos;u border):</span>
            <PostCard post={sampleExchangePost} />
          </div>
        </div>
      </section>

      {/* 5. FollowButton Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-okj-card-border pb-2">
          5. &lt;FollowButton /&gt; Komponenti (Optimistic UI holatlari)
        </h2>
        <div className="p-6 rounded-2xl bg-okj-card border border-okj-card-border flex flex-wrap items-center gap-6">
          <FollowButton userId="user-a" initialFollowing={false} />
          <FollowButton userId="user-b" initialFollowing={true} />
        </div>
      </section>

      {/* 6. IntentTag Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-okj-card-border pb-2">
          6. &lt;IntentTag /&gt; Komponenti
        </h2>
        <div className="p-6 rounded-2xl bg-okj-card border border-okj-card-border flex flex-wrap items-center gap-3">
          {['Barchasi', 'Iqtiboslar', 'Taqrizlar', 'Almashish'].map((tag) => (
            <IntentTag
              key={tag}
              type={tag}
              active={activeTag === tag}
              onClick={() => setActiveTag(tag)}
            />
          ))}
        </div>
      </section>

      {/* 7. SkeletonCard Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-okj-card-border pb-2">
          7. &lt;SkeletonCard /&gt; Komponenti (post | book | profile)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <span className="text-xs text-okj-text-muted font-mono block mb-2">post variant:</span>
            <SkeletonCard variant="post" />
          </div>
          <div>
            <span className="text-xs text-okj-text-muted font-mono block mb-2">book variant:</span>
            <SkeletonCard variant="book" />
          </div>
          <div>
            <span className="text-xs text-okj-text-muted font-mono block mb-2">profile variant:</span>
            <SkeletonCard variant="profile" />
          </div>
        </div>
      </section>
    </div>
  );
}
