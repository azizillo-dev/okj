'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';
import { BookOpen, Compass, Search, Bell, User, PlusCircle, Layers } from 'lucide-react';

export const Navbar: React.FC<{ onOpenCreateModal?: () => void }> = ({ onOpenCreateModal }) => {
  const pathname = usePathname();

  const navLinks = [
    { href: '/', label: 'Asosiy', icon: BookOpen },
    { href: '/feed', label: 'Lenta', icon: Compass },
    { href: '/search', label: 'Qidiruv', icon: Search },
    { href: '/notifications', label: 'Xabarlar', icon: Bell },
    { href: '/u/OKJ-10492', label: 'Pasport', icon: User },
    { href: '/dev/components', label: 'Dizayn', icon: Layers },
  ];

  return (
    <header className="sticky top-0 z-40 bg-okj-surface/90 backdrop-blur-md border-b border-okj-card-border">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 shrink-0 group">
          <div className="w-10 h-10 rounded-xl bg-okj-gold text-okj-bg-deep flex items-center justify-center font-display font-black text-xl shadow-md group-hover:scale-105 transition-transform">
            O
          </div>
          <div className="flex flex-col">
            <span className="font-display font-black text-lg tracking-tight text-okj-text-primary leading-none">
              OKJ
            </span>
            <span className="text-[10px] font-display uppercase tracking-widest text-okj-gold font-bold">
              PASSPORT
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  'flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-okj-card text-okj-gold border border-okj-card-border/60 font-bold'
                    : 'text-okj-text-secondary hover:text-okj-text-primary hover:bg-okj-card/50'
                )}
              >
                <Icon className={clsx('w-4 h-4', isActive && 'stroke-[2.5]')} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Create CTA Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenCreateModal}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-okj-gold text-okj-bg-deep font-display font-bold text-sm shadow-md hover:bg-okj-gold/90 transition-all active:scale-95 shrink-0"
          >
            <PlusCircle className="w-4 h-4 stroke-[2.5]" />
            <span className="hidden sm:inline">Post Yozish</span>
          </button>
        </div>
      </div>

      {/* Mobile Bottom Bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-okj-surface/95 backdrop-blur-lg border-t border-okj-card-border px-2 py-1.5 flex items-center justify-around">
        {navLinks.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'flex flex-col items-center justify-center py-1 px-3 rounded-xl text-[11px] font-medium transition-colors min-w-[56px]',
                isActive ? 'text-okj-gold' : 'text-okj-text-secondary'
              )}
            >
              <Icon className={clsx('w-5 h-5 mb-0.5', isActive ? 'stroke-[2.5]' : 'stroke-[1.5]')} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </header>
  );
};
