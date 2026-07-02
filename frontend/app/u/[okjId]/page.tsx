'use client';

import React, { use, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Trophy, BookOpen, Layers, Flame, Share2, Shield, Gift } from 'lucide-react';
import { passportApi } from '@/lib/api/passport';
import { PassportAnalytics } from '@/lib/api/types';
import { Avatar, PassportStamp, FollowButton, SkeletonCard } from '@/components/ui';
import { ReadingHeatmap, DailySpinWheel } from '@/components/ui/premium';
import { GlassButton } from '@/components/ui/glass';

export default function UserProfilePage({ params }: { params: Promise<{ okjId: string }> }) {
  const { okjId } = use(params);
  const [isSpinOpen, setIsSpinOpen] = useState(false);

  // Check if viewing self vs someone else
  const isSelf = okjId === 'OKJ-10492' || okjId === 'me';

  const { data: passport, isLoading } = useQuery<PassportAnalytics>({
    queryKey: ['passport', okjId],
    queryFn: async () => {
      try {
        return await passportApi.getUserPassport(okjId);
      } catch {
        // Fallback realistic demo passport data
        return {
          okj_id: okjId,
          user: {
            id: 'u-10492',
            username: 'alisher_rustamov',
            first_name: 'Alisher',
            last_name: 'Rustamov',
            okj_id: okjId,
            total_xp: 1450,
            level: 14,
            bio: 'O\'zbek va jahon klassikasiga oshiq kitobxon. Tarixiy romanlar va falsafiy esselar o\'qiyman.',
            streak_days: 12,
          },
          books_read_count: 28,
          pages_read_count: 8420,
          current_streak: 12,
          stamps: [
            { id: 's1', icon: '🏛️', label: 'Tarix Bilag\'oni', locked: false },
            { id: 's2', icon: '🔥', label: '7 kunlik o\'qish', locked: false },
            { id: 's3', icon: '✍️', label: '10 ta iqtibos', locked: false },
            { id: 's4', icon: '🔁', label: 'Kitob Almashuvchi', locked: false },
            { id: 's5', icon: '🌟', label: 'G\'azalxon', locked: false },
            { id: 's6', icon: '📚', label: '100 ta Kitob', locked: true },
            { id: 's7', icon: '⚡', label: '30 Kunlik Seriya', locked: true },
            { id: 's8', icon: '💎', label: 'Afsonaviy Taqrizchi', locked: true },
          ],
        };
      }
    },
  });

  // Mock 365 days contribution data for demo
  const sampleContributions = React.useMemo(() => {
    const today = new Date();
    const list = [];
    for (let i = 0; i < 365; i++) {
      const d = new Date(today);
      d.setDate(d.getDate() - (365 - i));
      const dateStr = d.toISOString().split('T')[0];
      // Generate realistic reading patterns
      const isWeekend = d.getDay() === 0 || d.getDay() === 6;
      const pages = Math.random() > 0.4 ? (isWeekend ? Math.floor(Math.random() * 85) + 20 : Math.floor(Math.random() * 45)) : 0;
      if (pages > 0) {
        list.push({
          date: dateStr,
          pagesRead: pages,
          xpEarned: Math.floor(pages * 0.7),
          bookTitle: pages > 50 ? 'Yulduzli tunlar' : 'O\'tkan kunlar',
        });
      }
    }
    return list;
  }, []);

  if (isLoading || !passport) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <SkeletonCard variant="profile" />
      </div>
    );
  }

  const level = passport.user.level || Math.floor((passport.user.total_xp || 0) / 100);
  const currentXpInLevel = (passport.user.total_xp || 0) % 100;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Electronic Passport Header Card */}
      <div className="relative p-6 md:p-8 rounded-3xl bg-gradient-to-br from-okj-card via-okj-surface to-okj-card border-2 border-okj-gold/40 shadow-2xl overflow-hidden">
        {/* Decorative background badge */}
        <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none text-okj-gold">
          <Shield className="w-80 h-80" />
        </div>

        <div className="relative z-10 flex flex-col md:flex-row items-center md:items-start gap-6">
          <Avatar user={passport.user} size="lg" className="border-2 border-okj-gold shadow-lg" />

          <div className="flex-1 text-center md:text-left space-y-3">
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
              <span className="px-3 py-1 rounded-full bg-okj-gold text-okj-bg-deep font-display font-black text-xs tracking-widest uppercase">
                {passport.okj_id}
              </span>
              <span className="text-xs text-okj-text-secondary font-mono">Daraja: {level}-Level</span>
            </div>

            <h1 className="font-display font-black text-2xl md:text-3xl text-okj-text-primary">
              {passport.user.first_name} {passport.user.last_name}
            </h1>

            {passport.user.bio && (
              <p className="text-sm text-okj-text-secondary max-w-xl font-body">{passport.user.bio}</p>
            )}

            {/* Level Progress Bar */}
            <div className="max-w-md pt-2 space-y-1.5">
              <div className="flex justify-between text-xs font-display font-bold">
                <span className="text-okj-gold">{passport.user.total_xp} XP</span>
                <span className="text-okj-text-muted">Keyingi darajagacha {100 - currentXpInLevel} XP</span>
              </div>
              <div className="w-full h-2 rounded-full bg-okj-bg-deep overflow-hidden p-0.5 border border-okj-card-border">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-okj-terracotta to-okj-gold transition-all duration-500"
                  style={{ width: `${currentXpInLevel}%` }}
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="shrink-0 flex flex-col sm:flex-row items-center gap-3">
            {isSelf && (
              <GlassButton variant="gold" size="sm" onClick={() => setIsSpinOpen(true)}>
                <Gift className="w-4 h-4" />
                <span>Kunlik G&apos;ildirak</span>
              </GlassButton>
            )}
            {!isSelf ? (
              <FollowButton userId={passport.user.id} />
            ) : (
              <span className="px-4 py-2 rounded-xl bg-okj-surface border border-okj-card-border text-xs font-display font-bold text-okj-gold">
                Mening Pasportim
              </span>
            )}
            <button className="p-2.5 rounded-xl bg-okj-surface border border-okj-card-border text-okj-text-secondary hover:text-okj-text-primary transition-colors">
              <Share2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Quick Analytics Row */}
        <div className="mt-8 pt-6 border-t border-okj-card-border/60 grid grid-cols-3 gap-4 text-center relative z-10">
          <div className="p-3 rounded-2xl bg-okj-bg-deep/50">
            <div className="flex items-center justify-center gap-1.5 text-okj-gold mb-1">
              <BookOpen className="w-4 h-4" />
              <span className="font-display font-black text-xl">{passport.books_read_count}</span>
            </div>
            <div className="text-xs text-okj-text-secondary">O&apos;qilgan kitoblar</div>
          </div>
          <div className="p-3 rounded-2xl bg-okj-bg-deep/50">
            <div className="flex items-center justify-center gap-1.5 text-okj-gold mb-1">
              <Layers className="w-4 h-4" />
              <span className="font-display font-black text-xl">{passport.pages_read_count.toLocaleString()}</span>
            </div>
            <div className="text-xs text-okj-text-secondary">O&apos;qilgan sahifalar</div>
          </div>
          <div className="p-3 rounded-2xl bg-okj-bg-deep/50">
            <div className="flex items-center justify-center gap-1.5 text-okj-gold mb-1">
              <Flame className="w-4 h-4 fill-okj-gold" />
              <span className="font-display font-black text-xl">{passport.current_streak}</span>
            </div>
            <div className="text-xs text-okj-text-secondary">Kunlik seriya</div>
          </div>
        </div>
      </div>

      {/* GitHub-style 365-day Reading Heatmap */}
      <ReadingHeatmap contributions={sampleContributions} year={new Date().getFullYear()} />

      {/* Passport Stamps Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-display font-bold text-xl text-okj-text-primary flex items-center gap-2">
            <Trophy className="w-5 h-5 text-okj-gold" />
            <span>Pasport Muhrlari (Stamps)</span>
          </h2>
          <span className="text-xs text-okj-text-muted">
            {passport.stamps.filter((s) => !s.locked).length} / {passport.stamps.length} ta olingan
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-4 p-6 rounded-3xl bg-okj-card border border-okj-card-border justify-items-center">
          {passport.stamps.map((stamp) => (
            <PassportStamp key={stamp.id} icon={stamp.icon} label={stamp.label} locked={stamp.locked} />
          ))}
        </div>
      </div>

      {/* Duolingo Daily Spin Wheel Modal */}
      <DailySpinWheel
        isOpen={isSpinOpen}
        onClose={() => setIsSpinOpen(false)}
        onRequestSpin={async () => {
          // Simulate API call resolving to reward index 1 (+100 XP)
          return new Promise((resolve) => setTimeout(() => resolve(1), 300));
        }}
      />
    </div>
  );
}
