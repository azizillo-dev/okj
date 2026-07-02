'use client';

import React, { useState, useRef } from 'react';
import Image from 'next/image';
import { Camera, Upload, Check, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Avatar } from '@/components/ui';
import { authApi } from '@/lib/api/auth';

export default function SettingsPage() {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [formData, setFormData] = useState({
    firstName: 'Alisher',
    lastName: 'Rustamov',
    bio: 'O\'zbek va jahon klassikasiga oshiq kitobxon. Tarixiy romanlar va falsafiy esselar o\'qiyman.',
  });

  // Client-side image compress & crop via HTML5 Canvas (Requirement 3)
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setErrorMsg('Iltimos, faqat rasm faylini tanlang (JPG, PNG, WEBP).');
      return;
    }

    setIsProcessing(true);
    setErrorMsg(null);
    setUploadSuccess(false);

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new window.Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const size = Math.min(img.width, img.height);
        const targetSize = 400; // Standardize square avatar to 400x400

        canvas.width = targetSize;
        canvas.height = targetSize;

        const offsetX = (img.width - size) / 2;
        const offsetY = (img.height - size) / 2;

        if (ctx) {
          // Crop square center and compress
          ctx.drawImage(img, offsetX, offsetY, size, size, 0, 0, targetSize, targetSize);
          const compressedDataUrl = canvas.toDataURL('image/jpeg', 0.82); // 82% quality compression
          setPreviewUrl(compressedDataUrl);
          setIsProcessing(false);
        }
      };
      img.src = event.target?.result as string;
    };
    reader.readAsDataURL(file);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setErrorMsg(null);
    setUploadSuccess(false);
    try {
      await authApi.updateProfile({
        first_name: formData.firstName,
        last_name: formData.lastName,
        bio: formData.bio,
      });
      if (previewUrl) {
        await authApi.updateAvatar(previewUrl);
      }
      setUploadSuccess(true);
    } catch (err: unknown) {
      setErrorMsg((err as { message?: string })?.message || "Saqlashda xatolik yuz berdi.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-8">
      <div className="border-b border-okj-card-border pb-4">
        <h1 className="font-display font-bold text-2xl text-okj-text-primary">Profil va Pasport Sozlamalari</h1>
        <p className="text-xs text-okj-text-secondary mt-1">Shaxsiy ma&apos;lumotlar va avatar rasmingizni tahrirlash</p>
      </div>

      <form onSubmit={handleSave} className="space-y-8">
        {/* Avatar Upload Card */}
        <div className="p-6 rounded-3xl bg-okj-card border border-okj-card-border flex flex-col sm:flex-row items-center gap-6">
          <div className="relative group">
            <div className="w-24 h-24 rounded-full overflow-hidden border-2 border-okj-gold bg-okj-surface flex items-center justify-center relative shadow-inner">
              {previewUrl ? (
                <Image src={previewUrl} alt="Avatar preview" fill className="object-cover" />
              ) : (
                <Avatar user={{ id: 'u-10492', first_name: formData.firstName, last_name: formData.lastName }} size="lg" className="w-full h-full" />
              )}
            </div>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="absolute bottom-0 right-0 p-2 rounded-full bg-okj-gold text-okj-bg-deep shadow-lg hover:scale-110 transition-transform"
            >
              <Camera className="w-4 h-4 stroke-[2.5]" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          <div className="flex-1 space-y-2 text-center sm:text-left">
            <h3 className="font-display font-bold text-base text-okj-text-primary">Elektron Pasport Surati</h3>
            <p className="text-xs text-okj-text-secondary leading-relaxed">
              Tanlangan rasm brauzeringizning o&apos;zida avtomatik 400x400 o&apos;lchamda kesiladi va siqiladi (Client-side compress).
            </p>
            <div className="pt-1 flex items-center justify-center sm:justify-start gap-3">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-okj-surface border border-okj-card-border text-xs font-medium text-okj-text-primary hover:border-okj-gold/50 transition-colors"
              >
                <Upload className="w-3.5 h-3.5 text-okj-gold" />
                <span>Rasm tanlash</span>
              </button>
              {previewUrl && (
                <button
                  type="button"
                  onClick={() => setPreviewUrl(null)}
                  className="inline-flex items-center gap-1 text-xs text-rose-400 hover:underline"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Asliga qaytarish</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Profile Info Form */}
        <div className="p-6 rounded-3xl bg-okj-card border border-okj-card-border space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
                Ism
              </label>
              <input
                type="text"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                className="w-full px-4 py-3 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
                Familiya
              </label>
              <input
                type="text"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                className="w-full px-4 py-3 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
              O\'zingiz haqingizda (Bio)
            </label>
            <textarea
              rows={3}
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              className="w-full px-4 py-3 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors resize-none"
            />
          </div>
        </div>

        {/* Submit Save */}
        <div className="flex items-center justify-between pt-2">
          {uploadSuccess ? (
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold animate-in fade-in">
              <Check className="w-4 h-4" />
              <span>O&apos;zgarishlar muvaffaqiyatli saqlandi!</span>
            </div>
          ) : <div />}

          <button
            type="submit"
            disabled={isProcessing}
            className="flex items-center gap-2 px-8 py-3 rounded-xl bg-okj-gold text-okj-bg-deep font-display font-bold text-sm shadow-lg hover:bg-okj-gold/90 transition-all active:scale-95 disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Saqlanmoqda...</span>
              </>
            ) : (
              <span>Saqlash</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
