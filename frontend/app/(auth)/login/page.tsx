'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Loader2, ArrowRight } from 'lucide-react';
import { setAccessToken } from '@/lib/api/client';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);

    try {
      // Simulate login token setting for standalone preview or actual API call
      setTimeout(() => {
        setAccessToken('mock_jwt_access_token');
        router.push('/feed');
      }, 800);
    } catch {
      setErrorMsg('Kirishda xatolik yuz berdi. Login yoki parolni tekshiring.');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md p-8 rounded-3xl bg-okj-card border border-okj-card-border shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-okj-gold text-okj-bg-deep mx-auto flex items-center justify-center font-display font-black text-2xl shadow-md">
            O
          </div>
          <h1 className="font-display font-bold text-2xl text-okj-text-primary">OKJ Tizimiga Kirish</h1>
          <p className="text-xs text-okj-text-secondary">Elektron pasportingiz va lentangizga qayting</p>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs text-center">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
              Login yoki Email
            </label>
            <input
              type="text"
              required
              placeholder="masalan: alisher_rustamov"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
              Parol
            </label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-okj-gold text-okj-bg-deep font-display font-black text-sm shadow-xl hover:bg-okj-gold/90 transition-all active:scale-98 disabled:opacity-50 mt-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <span>Kirish</span>
                <ArrowRight className="w-4 h-4 stroke-[2.5]" />
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-4 border-t border-okj-card-border/60 text-xs text-okj-text-secondary">
          Akkauntingiz yo&apos;qmi?{' '}
          <Link href="/register" className="text-okj-gold font-bold hover:underline">
            Pasport olish
          </Link>
        </div>
      </div>
    </div>
  );
}
