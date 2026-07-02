'use client';

import React from 'react';
import { Bell, Heart, MessageCircle, UserPlus, Trophy, CheckCircle2 } from 'lucide-react';
import { Avatar } from '@/components/ui';

export default function NotificationsPage() {
  const notifications = [
    {
      id: 'n1',
      type: 'STAMP',
      title: 'Yangi Pasport Muhriga ega bo\'ldingiz!',
      message: '"Tarix Bilag\'oni" muhrini (stamp) muvaffaqiyatli ochdingiz. +50 XP qo\'shildi.',
      time: '10 daqiqa oldin',
      unread: true,
      icon: Trophy,
      color: 'text-okj-gold bg-okj-gold/15 border-okj-gold/40',
    },
    {
      id: 'n2',
      type: 'LIKE',
      user: { id: 'u2', username: 'bookworm_uz', first_name: 'Malika', last_name: 'Saidova' },
      message: 'sening "Yulduzli tunlar" haqidagi taqrizingni yoqtirdi.',
      time: '1 soat oldin',
      unread: true,
      icon: Heart,
      color: 'text-rose-500 bg-rose-500/15 border-rose-500/30',
    },
    {
      id: 'n3',
      type: 'COMMENT',
      user: { id: 'u3', username: 'intellect_99', first_name: 'Sardor', last_name: 'Ismoilov' },
      message: 'taqrizingizga fikr bildirdi: "Haqiqatdan ham ajoyib asar!"',
      time: '2 soat oldin',
      unread: false,
      icon: MessageCircle,
      color: 'text-indigo-400 bg-indigo-500/15 border-indigo-500/30',
    },
    {
      id: 'n4',
      type: 'FOLLOW',
      user: { id: 'u4', username: 'kitob_muhlis', first_name: 'Bekzod', last_name: 'Aliyev' },
      message: 'seni obunachilar qatoriga qo\'shdi.',
      time: 'Kecha',
      unread: false,
      icon: UserPlus,
      color: 'text-emerald-400 bg-emerald-500/15 border-emerald-500/30',
    },
  ];

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-okj-card-border">
        <div className="flex items-center gap-2.5">
          <Bell className="w-6 h-6 text-okj-gold" />
          <h1 className="font-display font-bold text-2xl text-okj-text-primary">Xabarlar & Bildirishnomalar</h1>
        </div>
        <button className="flex items-center gap-1.5 text-xs text-okj-gold hover:underline font-medium">
          <CheckCircle2 className="w-4 h-4" />
          <span>Barchasini o&apos;qilgan deb belgilash</span>
        </button>
      </div>

      <div className="space-y-3">
        {notifications.map((notif) => {
          const Icon = notif.icon;
          return (
            <div
              key={notif.id}
              className={`p-4 rounded-2xl border transition-colors flex items-start gap-4 ${
                notif.unread
                  ? 'bg-okj-card border-okj-gold/40 shadow-md'
                  : 'bg-okj-surface/60 border-okj-card-border/60 opacity-85'
              }`}
            >
              <div className={`p-2.5 rounded-xl border shrink-0 ${notif.color}`}>
                <Icon className="w-5 h-5" />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  {notif.user ? (
                    <div className="flex items-center gap-2">
                      <Avatar user={notif.user} size="sm" />
                      <span className="font-display font-bold text-sm text-okj-text-primary">
                        {notif.user.first_name} {notif.user.last_name}
                      </span>
                    </div>
                  ) : (
                    <span className="font-display font-bold text-sm text-okj-gold">{notif.title}</span>
                  )}
                  <span className="text-xs text-okj-text-muted shrink-0">{notif.time}</span>
                </div>
                <p className="text-sm text-okj-text-secondary leading-relaxed">{notif.message}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
