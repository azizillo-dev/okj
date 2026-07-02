'use client';

import React, { useState } from 'react';
import clsx from 'clsx';
import { X, Quote, MessageCircle, Share2, Repeat, Gift, Tag, Loader2, BookOpen } from 'lucide-react';
import { PostType } from '@/lib/api/types';
import { postsApi } from '@/lib/api/posts';

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const POST_TYPES: { type: PostType; label: string; icon: any; color: string }[] = [
  { type: 'QUOTE', label: 'Iqtibos', icon: Quote, color: 'text-okj-gold bg-okj-gold/15' },
  { type: 'REVIEW', label: 'Taqriz', icon: MessageCircle, color: 'text-indigo-400 bg-indigo-500/15' },
  { type: 'SHOWCASE', label: 'Ko\'rgazma', icon: Share2, color: 'text-emerald-400 bg-emerald-500/15' },
  { type: 'EXCHANGE', label: 'Almashish', icon: Repeat, color: 'text-okj-terracotta bg-okj-terracotta/15' },
  { type: 'GIFT', label: 'Sovg\'a', icon: Gift, color: 'text-rose-400 bg-rose-500/15' },
  { type: 'SELL', label: 'Sotuv', icon: Tag, color: 'text-okj-terracotta bg-okj-terracotta/15' },
];

export const CreatePostModal: React.FC<CreatePostModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [postType, setPostType] = useState<PostType>('QUOTE');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [quotePage, setQuotePage] = useState<number | ''>('');
  const [price, setPrice] = useState<number | ''>('');
  const [bookQuery, setBookQuery] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      setErrorMsg('Iltimos, matnni kiritishni unutmang.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      await postsApi.createPost({
        post_type: postType,
        title: title || undefined,
        content,
        quote_page: quotePage !== '' ? Number(quotePage) : undefined,
        price: price !== '' ? Number(price) : undefined,
      });
      setContent('');
      setTitle('');
      setQuotePage('');
      setPrice('');
      onSuccess?.();
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Post yozishda xatolik yuz berdi.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isQuote = postType === 'QUOTE';
  const isExchangeOrSell = postType === 'EXCHANGE' || postType === 'SELL';

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg rounded-t-3xl sm:rounded-3xl bg-okj-surface border border-okj-card-border overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 sm:p-5 flex items-center justify-between border-b border-okj-card-border">
          <h3 className="font-display font-bold text-lg text-okj-text-primary flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-okj-gold" />
            <span>Yangi Kitobxon Fikri</span>
          </h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-okj-text-secondary hover:text-okj-text-primary hover:bg-okj-card transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-4 sm:p-5 overflow-y-auto space-y-4 flex-1">
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs font-medium">
              {errorMsg}
            </div>
          )}

          {/* Type Selection */}
          <div>
            <label className="block text-xs font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-2">
              Post Turi
            </label>
            <div className="grid grid-cols-3 gap-2">
              {POST_TYPES.map((t) => {
                const Icon = t.icon;
                const isSelected = postType === t.type;
                return (
                  <button
                    key={t.type}
                    type="button"
                    onClick={() => setPostType(t.type)}
                    className={clsx(
                      'flex items-center gap-2 p-2.5 rounded-xl text-xs font-medium border transition-all',
                      isSelected
                        ? 'bg-okj-card border-okj-gold text-okj-gold font-bold shadow'
                        : 'bg-okj-bg-deep/50 border-okj-card-border/60 text-okj-text-secondary hover:text-okj-text-primary'
                    )}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span className="truncate">{t.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Book Search Option */}
          <div>
            <label className="block text-xs font-medium text-okj-text-secondary mb-1">Kitobni tanlang (yoki qidirish)</label>
            <input
              type="text"
              placeholder="Masalan: Yulduzli tunlar..."
              value={bookQuery}
              onChange={(e) => setBookQuery(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors"
            />
          </div>

          {/* Optional Title */}
          {!isQuote && (
            <div>
              <label className="block text-xs font-medium text-okj-text-secondary mb-1">Sarlavha (ixtiyoriy)</label>
              <input
                type="text"
                placeholder="Taqriz sarlavhasi..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors"
              />
            </div>
          )}

          {/* Content Area */}
          <div>
            <label className="block text-xs font-display font-bold uppercase tracking-wider text-okj-text-secondary mb-1">
              {isQuote ? 'Iqtibos matni' : 'Fikr matni'} <span className="text-rose-400">*</span>
            </label>
            <textarea
              rows={4}
              placeholder={isQuote ? 'Sevimli kitobingizdan ta\'sirli satrlar...' : 'Kitob haqidagi taassurotlar...'}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              className={clsx(
                'w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm focus:outline-none focus:border-okj-gold transition-colors resize-none',
                isQuote ? 'font-display italic text-base text-okj-gold' : 'text-okj-text-primary'
              )}
            />
          </div>

          {/* Quote Page */}
          {isQuote && (
            <div>
              <label className="block text-xs font-medium text-okj-text-secondary mb-1">Sahifa raqami (ixtiyoriy)</label>
              <input
                type="number"
                placeholder="Masalan: 142"
                value={quotePage}
                onChange={(e) => setQuotePage(e.target.value !== '' ? Number(e.target.value) : '')}
                className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors"
              />
            </div>
          )}

          {/* Price */}
          {isExchangeOrSell && (
            <div>
              <label className="block text-xs font-medium text-okj-text-secondary mb-1">Narxi (UZS)</label>
              <input
                type="number"
                placeholder="Masalan: 45000"
                value={price}
                onChange={(e) => setPrice(e.target.value !== '' ? Number(e.target.value) : '')}
                className="w-full px-3.5 py-2.5 rounded-xl bg-okj-bg-deep border border-okj-card-border text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold transition-colors"
              />
            </div>
          )}

          {/* Submit */}
          <div className="pt-2 flex items-center justify-end gap-3 border-t border-okj-card-border/40">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-okj-card text-okj-text-secondary hover:text-okj-text-primary text-sm font-medium transition-colors"
            >
              Bekor qilish
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-okj-gold text-okj-bg-deep font-display font-bold text-sm shadow-md hover:bg-okj-gold/90 transition-all active:scale-95 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Nashr qilinmoqda...</span>
                </>
              ) : (
                <span>Nashr Qilish</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePostModal;
