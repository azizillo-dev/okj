import React from 'react';
import Link from 'next/link';
import { Sparkles, BookOpen, Users, Trophy, ArrowRight, ShieldCheck, Repeat } from 'lucide-react';

// Static SSG Landing page
export default function LandingPage() {
  const stats = [
    { label: "Ro'yxatdan o'tgan kitobxonlar", value: '24,500+' },
    { label: "O'qilgan kitoblar bazasi", value: '180,000+' },
    { label: 'Olingan pasport yutuqlari', value: '95,000+' },
    { label: 'Jamoaviy almashishlar', value: '12,400+' },
  ];

  const features = [
    {
      icon: Trophy,
      title: 'Elektron Pasport & Gamifikatsiya',
      desc: 'Har bir o\'qigan sahifangiz va kitobingiz uchun XP yig\'ing, daraja ko\'taring va nodir muhrlarga (stamps) ega bo\'ling.',
    },
    {
      icon: BookOpen,
      title: 'Markaziy Trigram Qidiruv',
      desc: 'Imlo xatoliklariga chidamli tezkor va aniq qidiruv orqali sevimli kitoblar va hamfikrlarni 300ms ichida toping.',
    },
    {
      icon: Repeat,
      title: 'Kitob Almashish & Ko\'rgazma',
      desc: 'O\'qib bo\'lingan kitoblaringizni boshqalarga almashtiring, sovg\'a qiling yoki iqtiboslaringiz bilan lentani bezang.',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <section className="relative pt-12 pb-20 md:pt-20 md:pb-32 overflow-hidden px-4">
        <div className="absolute inset-0 bg-gradient-to-b from-okj-surface/30 to-transparent pointer-events-none" />
        <div className="max-w-5xl mx-auto text-center relative z-10 space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-okj-gold/15 border border-okj-gold/30 text-okj-gold text-xs font-display font-bold uppercase tracking-widest">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Intellektual O&apos;zbekiston Poyeavori</span>
          </div>

          <h1 className="font-display font-black text-4xl sm:text-6xl md:text-7xl tracking-tight text-okj-text-primary leading-[1.1]">
            Kitobxonlikning <span className="text-okj-gold underline decoration-okj-terracotta/60">Yangi Davri</span>
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-okj-text-secondary leading-relaxed font-body">
            O&apos;zbekiston Kitobxonlari Jamiyati (OKJ) — bu kitob o&apos;qishni gamifikatsiya qilingan raqamli pasport, o\'zaro almashish va hamfikrlarning jonli lentasiga aylantiruvchi yagona platforma.
          </p>

          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/feed"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 rounded-2xl bg-okj-gold text-okj-bg-deep font-display font-black text-base shadow-xl shadow-okj-gold/20 hover:scale-[1.02] active:scale-98 transition-transform duration-200"
            >
              <span>Lentani Ko&apos;rish</span>
              <ArrowRight className="w-5 h-5 stroke-[2.5]" />
            </Link>
            <Link
              href="/register"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 rounded-2xl bg-okj-card text-okj-text-primary border border-okj-card-border hover:bg-okj-surface font-display font-bold text-base transition-colors duration-200"
            >
              Pasport Olish
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-okj-surface/50 border-y border-okj-card-border px-4">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {stats.map((item, idx) => (
            <div key={idx} className="p-4 space-y-1">
              <div className="font-display font-black text-3xl sm:text-4xl text-okj-gold">{item.value}</div>
              <div className="text-xs sm:text-sm text-okj-text-secondary">{item.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 max-w-6xl mx-auto px-4 space-y-12">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <h2 className="font-display font-bold text-3xl sm:text-4xl text-okj-text-primary">
            Nega aynan OKJ Platformasi?
          </h2>
          <p className="text-sm text-okj-text-secondary">
            Meta va Instagram infratuzilmasi andozalarida yaratilgan ilg&apos;or imkoniyatlar bilan tanishing.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-3xl bg-okj-card border border-okj-card-border flex flex-col gap-4 hover:border-okj-gold/40 transition-colors"
              >
                <div className="w-12 h-12 rounded-2xl bg-okj-surface border border-okj-card-border flex items-center justify-center text-okj-gold">
                  <Icon className="w-6 h-6 stroke-[2]" />
                </div>
                <h3 className="font-display font-bold text-xl text-okj-text-primary">{feat.title}</h3>
                <p className="text-sm text-okj-text-secondary leading-relaxed">{feat.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Bottom Call To Action */}
      <section className="py-16 max-w-4xl mx-auto px-4 w-full">
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-okj-card via-okj-surface to-okj-card border border-okj-gold/30 text-center space-y-6 shadow-2xl relative overflow-hidden">
          <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-okj-gold/10 rounded-full blur-3xl" />
          <h2 className="font-display font-black text-2xl sm:text-4xl text-okj-text-primary">
            O&apos;z Elektron Pasportingizni ochishga tayyormisiz?
          </h2>
          <p className="text-sm sm:text-base text-okj-text-secondary max-w-xl mx-auto">
            G&apos;oyalar almashing, kitob o&apos;qing va O&apos;zbekiston intellektual elitasining bir qismiga aylaning.
          </p>
          <div className="pt-2">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-okj-gold text-okj-bg-deep font-display font-black text-base shadow-xl hover:bg-okj-gold/90 transition-all"
            >
              Ro&apos;yxatdan O&apos;tish
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
