'use client';

import React, { useState } from 'react';
import { Layers, Sparkles } from 'lucide-react';
import { PostCard } from '@/components/ui';
import { BookCover3D, ReadingHeatmap, DailySpinWheel } from '@/components/ui/premium';
import { GlassCard, GlassButton, GlassBadge, GlassInput, GlassChip, GlassProgress } from '@/components/ui/glass';
import { Post, Book } from '@/lib/api/types';

export default function ComponentsPreviewPage() {
  const [isSpinOpen, setIsSpinOpen] = useState(false);

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

  const sampleHeatmapData = React.useMemo(() => {
    const list = [];
    const today = new Date();
    for (let i = 0; i < 365; i++) {
      const d = new Date(today);
      d.setDate(d.getDate() - (365 - i));
      const hashVal = ((i * 12345 + 6789) % 100000) / 100000;
      const pages = hashVal > 0.45 ? Math.floor(hashVal * 70) : 0;
      if (pages > 0) {
        list.push({ date: d.toISOString().split('T')[0], pagesRead: pages, xpEarned: Math.floor(pages * 0.8) });
      }
    }
    return list;
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-12">
      {/* Header */}
      <GlassCard variant="prominent" className="p-6 md:p-8 space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-okj-gold/15 text-okj-gold text-xs font-display font-bold uppercase tracking-widest">
          <Layers className="w-3.5 h-3.5" />
          <span>Design Systems Showcase</span>
        </div>
        <h1 className="font-display font-black text-3xl md:text-4xl text-okj-text-primary">
          OKJ 10X Premium UI & Glass Primitivlar Katalogi
        </h1>
        <p className="text-sm text-okj-text-secondary max-w-2xl font-body">
          Bu sahifada barcha Apple VisionOS Glass Primitivlar hamda 3D Kitob muqovasi, GitHub Heatmap va Duolingo G&apos;ildiragi namoyish etilgan.
        </p>
      </GlassCard>

      {/* NEW 1: 3D Book Cover Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-white/10 pb-2 flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          <span>NEW 1. &lt;BookCover3D /&gt; Komponenti (Pure CSS 3D Perspective & Spine)</span>
        </h2>
        <div className="p-8 rounded-3xl bg-okj-surface/40 border border-white/10 flex flex-wrap items-center justify-around gap-8">
          <div className="text-center">
            <BookCover3D book={sampleBook} />
            <span className="text-xs text-okj-text-muted font-mono block mt-2">Hover qiling (3D Tilt)</span>
          </div>
          <div className="text-center">
            <BookCover3D book={{ ...sampleBook, title: 'O\'tkan kunlar', authors: [{ id: '2', name: 'Abdulla Qodiriy' }] }} />
            <span className="text-xs text-okj-text-muted font-mono block mt-2">2-kitob muqovasi</span>
          </div>
        </div>
      </section>

      {/* NEW 2: Reading Heatmap Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-white/10 pb-2 flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          <span>NEW 2. &lt;ReadingHeatmap /&gt; Komponenti (365 kunlik GitHub Uslubi)</span>
        </h2>
        <ReadingHeatmap contributions={sampleHeatmapData} year={new Date().getFullYear()} />
      </section>

      {/* NEW 3: Daily Spin Wheel Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-white/10 pb-2 flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          <span>NEW 3. &lt;DailySpinWheel /&gt; Komponenti (Framer Motion & Confetti)</span>
        </h2>
        <GlassCard className="p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h4 className="font-display font-bold text-lg text-okj-text-primary">Kunlik Omad G&apos;ildiragi Testi</h4>
            <p className="text-xs text-okj-text-secondary">
              G&apos;ildirakni aylantiring, backend javobiga ko&apos;ra to&apos;xtaydi va Confetti otiladi.
            </p>
          </div>
          <GlassButton variant="gold" size="md" onClick={() => setIsSpinOpen(true)}>
            G&apos;ildirakni Ochish
          </GlassButton>
        </GlassCard>
        <DailySpinWheel
          isOpen={isSpinOpen}
          onClose={() => setIsSpinOpen(false)}
          onRequestSpin={async () => new Promise((res) => setTimeout(() => res(1), 300))}
        />
      </section>

      {/* NEW 4: Glass Primitives Showcase */}
      <section className="space-y-4">
        <h2 className="font-display font-bold text-xl text-okj-gold border-b border-white/10 pb-2">
          NEW 4. Apple VisionOS Glass Primitives (&lt;GlassCard /&gt;, &lt;GlassButton /&gt;)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <GlassCard variant="subtle" className="p-5">
            <h4 className="font-display font-bold text-sm text-okj-text-primary">Subtle GlassCard</h4>
            <p className="text-xs text-okj-text-secondary mt-1">Yengil blur va shaffof chegara.</p>
          </GlassCard>
          <GlassCard variant="default" interactive className="p-5">
            <h4 className="font-display font-bold text-sm text-okj-text-primary">Default Interactive</h4>
            <p className="text-xs text-okj-text-secondary mt-1">Hover qilinganda ko&apos;tariladi.</p>
          </GlassCard>
          <GlassCard variant="prominent" className="p-5">
            <h4 className="font-display font-bold text-sm text-okj-gold">Prominent Gold Glow</h4>
            <p className="text-xs text-okj-text-secondary mt-1">Tilla chet va chuqur shisha nuri.</p>
          </GlassCard>
        </div>
        <div className="flex flex-wrap gap-4 pt-2">
          <GlassButton variant="primary">Primary GlassButton</GlassButton>
          <GlassButton variant="secondary">Secondary GlassButton</GlassButton>
          <GlassButton variant="gold">Gold GlassButton</GlassButton>
          <GlassButton variant="ghost">Ghost Button</GlassButton>
        </div>
        <div className="pt-4 space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <GlassBadge variant="gold">👑 VIP Kitobxon</GlassBadge>
            <GlassBadge variant="success">Yaxshi holatda</GlassBadge>
            <GlassBadge variant="default">Almashish</GlassBadge>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <GlassChip active>Barchasi</GlassChip>
            <GlassChip>Iqtiboslar</GlassChip>
            <GlassChip>Taqrizlar</GlassChip>
          </div>
          <div className="max-w-md space-y-2">
            <span className="text-xs text-okj-text-secondary">O&apos;qish darajasi (72%)</span>
            <GlassProgress value={72} />
          </div>
          <div className="max-w-md">
            <GlassInput placeholder="Kitob yoki muallif qidirish..." />
          </div>
        </div>
      </section>

      {/* Existing Components */}
      <section className="space-y-4 pt-6 border-t border-white/10">
        <h2 className="font-display font-bold text-xl text-okj-text-secondary pb-2">
          Mavjud Asosiy UI Komponentlar
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <PostCard post={sampleQuotePost} />
          <PostCard post={sampleExchangePost} />
        </div>
      </section>
    </div>
  );
}
