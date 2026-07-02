'use client';

import React from 'react';
import Link from 'next/link';
import { AlertTriangle, WifiOff, ShieldAlert, FileQuestion, RefreshCw, Home } from 'lucide-react';
import { GlassCard, GlassButton } from '@/components/ui/glass';

export type ErrorStateVariant = '404' | '403' | '500' | 'offline' | 'network' | 'generic';

interface GlassErrorStateProps {
  variant?: ErrorStateVariant;
  title?: string;
  description?: string;
  error?: Error & { digest?: string };
  onRetry?: () => void;
  showHomeButton?: boolean;
}

/**
 * Enterprise Production-Ready Glass Error State component.
 * Handles 404, 403, 500, Offline, and Network Errors with Apple VisionOS glassmorphism.
 */
export const GlassErrorState: React.FC<GlassErrorStateProps> = ({
  variant = 'generic',
  title,
  description,
  error,
  onRetry,
  showHomeButton = true,
}) => {
  const config = {
    '404': {
      icon: FileQuestion,
      color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      defaultTitle: 'Sahifayoki Kitob Topilmadi',
      defaultDesc: "Siz qidirayotgan manzil mavjud emas yoki o'chirilgan bo'lishi mumkin.",
    },
    '403': {
      icon: ShieldAlert,
      color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
      defaultTitle: "Ruxsat Cheklangan (403)",
      defaultDesc: "Ushbu bo'limga kirish yoki bu amalni bajarish uchun sizda yetarli huquq yo'q.",
    },
    '500': {
      icon: AlertTriangle,
      color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
      defaultTitle: 'Tizimda Xatolik Yuz Berdi',
      defaultDesc: "Serverimizda kutilmagan xatolik yuz berdi. Muhandislarimiz allaqachon bundan xabardor.",
    },
    offline: {
      icon: WifiOff,
      color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
      defaultTitle: "Internet Aloqasi Yo'q",
      defaultDesc: "Tarmoqqa ulanish yo'qolgan ko'rinadi. Iltimos, internet aloqangizni tekshiring.",
    },
    network: {
      icon: RefreshCw,
      color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      defaultTitle: 'Tarmoqqa Ulanishda Xato',
      defaultDesc: "Server bilan aloqa o'rnatib bo'lmadi. Aloqa sekinligi yoki server bandligi sabab bo'lishi mumkin.",
    },
    generic: {
      icon: AlertTriangle,
      color: 'text-okj-gold bg-okj-gold/10 border-okj-gold/30',
      defaultTitle: 'Kutilmagan Xatolik',
      defaultDesc: "Sahifani yuklash jarayonida xatolik sodir bo'ldi.",
    },
  }[variant];

  const IconComponent = config.icon;
  const displayTitle = title || config.defaultTitle;
  const displayDesc = description || config.defaultDesc;

  return (
    <div className="min-h-[60vh] flex items-center justify-center p-4">
      <GlassCard variant="prominent" className="max-w-md w-full p-8 text-center space-y-6 relative overflow-hidden shadow-2xl animate-fadeIn">
        {/* Glowing background halo */}
        <div className="absolute -top-16 -left-16 w-32 h-32 rounded-full bg-okj-gold/10 blur-3xl pointer-events-none" />

        {/* Icon Circle */}
        <div className={`w-20 h-20 mx-auto rounded-3xl flex items-center justify-center border shadow-inner ${config.color}`}>
          <IconComponent className="w-10 h-10" />
        </div>

        {/* Text Content */}
        <div className="space-y-2">
          <h2 className="font-display font-bold text-xl md:text-2xl text-okj-text-primary">{displayTitle}</h2>
          <p className="text-xs md:text-sm text-okj-text-secondary leading-relaxed">{displayDesc}</p>
          {error?.digest && (
            <p className="text-[10px] font-mono text-okj-text-muted pt-2">
              Xato kodi (Digest): <span className="text-okj-gold">{error.digest}</span>
            </p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-okj-gold hover:bg-okj-gold-light text-okj-bg-deep font-display font-bold text-xs flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-okj-gold/20"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Qaytadan urinish</span>
            </button>
          )}

          {showHomeButton && (
            <Link href="/" className="w-full sm:w-auto">
              <GlassButton variant="secondary" className="w-full flex items-center justify-center gap-2 text-xs py-2.5">
                <Home className="w-4 h-4" />
                <span>Bosh sahifa</span>
              </GlassButton>
            </Link>
          )}
        </div>
      </GlassCard>
    </div>
  );
};
