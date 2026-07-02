'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Shield, Loader2, ArrowRight } from 'lucide-react';
import { setAccessToken } from '@/lib/api/client';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    firstName: '',
    lastName: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    setTimeout(() => {
      setAccessToken('mock_jwt_access_token');
      router.push('/u/OKJ-10492');
    }, 1000);
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md p-8 rounded-3xl bg-okj-card border border-okj-card-border shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-okj-gold text-okj-bg-deep mx-auto flex items-center justify-center font-display font-black text-2xl shadow-md">
            <Shield className="w-6 h-6 stroke-[2.5]" />
          </div>
          <h1 className="font-display font-bold text-2xl text-okj-text-primary">Elektron Pasport Olish</h1>
          <p className="text-xs text-okj-text-secondary">OKJ jamiyatiga a&apos;zo bo&apos;ling va statistikangizni boshlang</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-3.5">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
                Ism
              </label>
              <input
                type="text"
                required
                placeholder="Alisher"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold"
              />
            </div>
            <div>
              <label className="block text-[11px] font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
                Familiya
              </label>
              <input
                type="text"
                required
                placeholder="Rustamov"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
              Foydalanuvchi nomi (Username)
            </label>
            <input
              type="text"
              required
              placeholder="alisher_rustamov"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold"
            />
          </div>

          <div>
            <label className="block text-[11px] font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
              Email manzil
            </label>
            <input
              type="email"
              required
              placeholder="alisher@example.uz"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold"
            />
          </div>

          <div>
            <label className="block text-[11px] font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
              Parol o&apos;ylab toping
            </label>
            <input
              type="password"
              required
              placeholder="Kamida 8 ta belgi"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-okj-gold text-okj-bg-deep font-display font-black text-sm shadow-xl hover:bg-okj-gold/90 transition-all active:scale-98 disabled:opacity-50 mt-4"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <span>Pasportni Yaratish</span>
                <ArrowRight className="w-4 h-4 stroke-[2.5]" />
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-4 border-t border-okj-card-border/60 text-xs text-okj-text-secondary">
          Allaqachon pasportingiz bormi?{' '}
          <Link href="/login" className="text-okj-gold font-bold hover:underline">
            Kirish
          </Link>
        </div>
      </div>
    </div>
  );
}
