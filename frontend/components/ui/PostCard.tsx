'use client';

import React, { useState, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Heart,
  MessageCircle,
  Share2,
  Quote,
  Tag,
  Gift,
  Repeat,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  Copy,
  Send,
  Check,
} from 'lucide-react';
import { Post } from '@/lib/api/types';
import { Avatar } from './Avatar';
import { postsApi } from '@/lib/api/posts';
import { GlassBottomSheet, GlassButton } from '@/components/ui/glass';

interface PostCardProps {
  post: Post;
  onLikeToggle?: (postId: string, newLiked: boolean, newCount: number) => void;
}

export const PostCard: React.FC<PostCardProps> = React.memo(({ post, onLikeToggle }) => {
  const [isLiked, setIsLiked] = useState(post.is_liked_by_user || false);
  const [likesCount, setLikesCount] = useState(post.likes_count || 0);
  const [isLiking, setIsLiking] = useState(false);

  const [isBookmarked, setIsBookmarked] = useState(false);
  const [showHeartAnim, setShowHeartAnim] = useState(false);
  const [currentMediaIdx, setCurrentMediaIdx] = useState(0);
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [showCommentsPreview, setShowCommentsPreview] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  const lastTapRef = useRef<number>(0);

  const handleLike = async (forcedValue?: boolean) => {
    if (isLiking) return;
    const prevLiked = isLiked;
    const prevCount = likesCount;

    const nextLiked = forcedValue !== undefined ? forcedValue : !prevLiked;
    if (nextLiked === prevLiked) return;

    const nextCount = nextLiked ? prevCount + 1 : Math.max(0, prevCount - 1);

    setIsLiked(nextLiked);
    setLikesCount(nextCount);
    onLikeToggle?.(post.id, nextLiked, nextCount);

    setIsLiking(true);
    try {
      const result = await postsApi.likePost(post.id);
      setIsLiked(result.liked);
      setLikesCount(result.likes_count);
    } catch {
      setIsLiked(prevLiked);
      setLikesCount(prevCount);
      onLikeToggle?.(post.id, prevLiked, prevCount);
    } finally {
      setIsLiking(false);
    }
  };

  const handleDoubleTap = () => {
    const now = Date.now();
    const DOUBLE_TAP_DELAY = 300;
    if (now - lastTapRef.current < DOUBLE_TAP_DELAY) {
      setShowHeartAnim(true);
      setTimeout(() => setShowHeartAnim(false), 800);
      if (!isLiked) {
        handleLike(true);
      }
    }
    lastTapRef.current = now;
  };

  const toggleBookmark = () => {
    setIsBookmarked((prev) => !prev);
  };

  const handleCopyLink = () => {
    navigator.clipboard?.writeText(window.location.origin + `/posts/${post.id}`);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const isQuote = post.post_type === 'QUOTE';
  const isExchangeOrSell = post.post_type === 'EXCHANGE' || post.post_type === 'SELL';

  const typeBadge = {
    QUOTE: { label: 'Iqtibos', icon: Quote, color: 'text-okj-gold bg-okj-gold/10' },
    REVIEW: { label: 'Taqriz', icon: MessageCircle, color: 'text-indigo-400 bg-indigo-500/10' },
    SHOWCASE: { label: "Ko'rgazma", icon: Share2, color: 'text-emerald-400 bg-emerald-500/10' },
    EXCHANGE: { label: 'Almashish', icon: Repeat, color: 'text-okj-terracotta bg-okj-terracotta/10' },
    GIFT: { label: "Sovg'a", icon: Gift, color: 'text-rose-400 bg-rose-500/10' },
    SELL: { label: 'Sotuvda', icon: Tag, color: 'text-okj-terracotta bg-okj-terracotta/10' },
  }[post.post_type] || { label: post.post_type, icon: MessageCircle, color: 'text-okj-text-secondary bg-okj-surface' };

  const IconComponent = typeBadge.icon;

  return (
    <article
      className={clsx(
        'rounded-2xl border transition-colors duration-200 overflow-hidden relative select-none',
        isQuote
          ? 'bg-okj-parchment text-okj-parchment-text border-okj-gold/30 shadow-md'
          : 'bg-okj-card text-okj-text-primary border-okj-card-border',
        isExchangeOrSell && !isQuote && 'border-l-4 border-l-okj-terracotta'
      )}
      role="article"
      aria-label={`${post.user.first_name} tomonidan yozilgan ${typeBadge.label} posti`}
    >
      {/* Header */}
      <div className="p-4 flex items-center justify-between gap-3 border-b border-okj-card-border/20">
        <Link href={`/u/${post.user.okj_id || post.user.id}`} className="flex items-center gap-3 min-w-0 group">
          <Avatar user={post.user} size="sm" />
          <div className="min-w-0">
            <h4
              className={clsx(
                'font-display font-bold text-sm truncate group-hover:underline',
                isQuote ? 'text-okj-parchment-text' : 'text-okj-text-primary'
              )}
            >
              {post.user.first_name} {post.user.last_name || post.user.username}
            </h4>
            <p className={clsx('text-xs truncate', isQuote ? 'text-okj-parchment-text/70' : 'text-okj-text-secondary')}>
              {post.user.okj_id ? `${post.user.okj_id} • ` : ''}
              {new Date(post.created_at).toLocaleDateString('uz-UZ', { month: 'short', day: 'numeric' })}
            </p>
          </div>
        </Link>

        <span className={clsx('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium shrink-0', typeBadge.color)}>
          <IconComponent className="w-3.5 h-3.5" />
          <span>{typeBadge.label}</span>
        </span>
      </div>

      {/* Book Reference if available */}
      {post.book && (
        <div className={clsx('px-4 pt-3 pb-1 text-xs font-medium flex items-center gap-2', isQuote ? 'text-okj-parchment-text/80' : 'text-okj-gold')}>
          <span>Kitob:</span>
          <Link href={`/books/${post.book.slug}`} className="hover:underline font-bold">
            {post.book.title}
          </Link>
          {post.quote_page && <span>({post.quote_page}-sahifa)</span>}
        </div>
      )}

      {/* Interactive Content Body with Double Tap detection */}
      <div className="p-4 relative cursor-pointer" onClick={handleDoubleTap}>
        {post.title && (
          <h3 className={clsx('font-display font-bold text-base mb-2', isQuote ? 'text-okj-parchment-text' : 'text-okj-text-primary')}>
            {post.title}
          </h3>
        )}

        {isQuote ? (
          <blockquote className="font-display italic text-lg leading-relaxed border-l-2 border-okj-gold/60 pl-4 py-1 my-2">
            &quot;{post.content}&quot;
          </blockquote>
        ) : (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{post.content}</p>
        )}

        {isExchangeOrSell && post.price && (
          <div className="mt-3 inline-block px-3 py-1 rounded-lg bg-okj-terracotta/15 text-okj-terracotta font-bold text-sm">
            Narxi: {post.price.toLocaleString()} UZS
          </div>
        )}

        {/* Double Tap Heart Pop Animation */}
        <AnimatePresence>
          {showHeartAnim && (
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1.6, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.35, type: 'spring' }}
              className="absolute inset-0 flex items-center justify-center pointer-events-none z-20"
            >
              <Heart className="w-20 h-20 fill-rose-500 text-rose-500 drop-shadow-2xl" />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Media Attachments Carousel */}
      {post.media && post.media.length > 0 && (
        <div className="relative w-full aspect-video bg-okj-surface overflow-hidden group cursor-pointer" onClick={handleDoubleTap}>
          <Image
            src={post.media[currentMediaIdx].file_url}
            alt={`Post attachment ${currentMediaIdx + 1}`}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 640px"
          />

          {/* Carousel Navigation Buttons */}
          {post.media.length > 1 && (
            <>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setCurrentMediaIdx((prev) => (prev > 0 ? prev - 1 : post.media.length - 1));
                }}
                className="absolute left-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                aria-label="Oldingi rasm"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setCurrentMediaIdx((prev) => (prev < post.media.length - 1 ? prev + 1 : 0));
                }}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                aria-label="Keyingi rasm"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
              <div className="absolute bottom-2 inset-x-0 flex justify-center gap-1.5">
                {post.media.map((_, i) => (
                  <span
                    key={i}
                    className={clsx('w-1.5 h-1.5 rounded-full transition-all', i === currentMediaIdx ? 'w-4 bg-okj-gold' : 'bg-white/60')}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Footer / Instagram Actions Bar */}
      <div
        className={clsx(
          'px-4 py-3 flex items-center justify-between text-xs border-t',
          isQuote ? 'border-okj-gold/20 text-okj-parchment-text/80' : 'border-okj-card-border/40 text-okj-text-secondary'
        )}
      >
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={() => handleLike()}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-colors active:scale-95',
              isLiked
                ? 'text-rose-500 bg-rose-500/10 font-bold'
                : isQuote
                ? 'hover:bg-okj-parchment-text/10'
                : 'hover:bg-okj-surface'
            )}
            aria-label="Like bosish"
          >
            <Heart className={clsx('w-4 h-4', isLiked && 'fill-rose-500')} />
            <span>{likesCount}</span>
          </button>

          <button
            type="button"
            onClick={() => setShowCommentsPreview((prev) => !prev)}
            className={clsx('flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-colors', isQuote ? 'hover:bg-okj-parchment-text/10' : 'hover:bg-okj-surface')}
            aria-label="Fikrlarni ko'rish"
          >
            <MessageCircle className="w-4 h-4" />
            <span>{post.comments_count || 0}</span>
          </button>

          <button
            type="button"
            onClick={() => setIsShareOpen(true)}
            className={clsx('p-1.5 rounded-full transition-colors', isQuote ? 'hover:bg-okj-parchment-text/10' : 'hover:bg-okj-surface')}
            aria-label="Ulashish"
          >
            <Share2 className="w-4 h-4" />
          </button>
        </div>

        <button
          type="button"
          onClick={toggleBookmark}
          className={clsx(
            'p-1.5 rounded-full transition-colors active:scale-95',
            isBookmarked ? 'text-okj-gold' : isQuote ? 'hover:bg-okj-parchment-text/10' : 'hover:bg-okj-surface'
          )}
          aria-label="Saqlab qo'yish"
        >
          <Bookmark className={clsx('w-4 h-4', isBookmarked && 'fill-okj-gold')} />
        </button>
      </div>

      {/* Comments Preview Panel */}
      <AnimatePresence>
        {showCommentsPreview && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-4 pb-3 pt-1 border-t border-okj-card-border/20 space-y-2 text-xs overflow-hidden"
          >
            <div className="flex items-start gap-2">
              <span className="font-bold text-okj-gold">kitobxon_uz:</span>
              <span className={isQuote ? 'text-okj-parchment-text' : 'text-okj-text-secondary'}>
                G&apos;oyat ajoyib fikr! Ushbu asarni o&apos;qib tugatgach mendan ham shunga o&apos;xshash xulosalar tug&apos;ilgan edi.
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold text-indigo-400">ilmnuri_22:</span>
              <span className={isQuote ? 'text-okj-parchment-text' : 'text-okj-text-secondary'}>
                Albatta tavsiya eting, o&apos;qishlar ro&apos;yxatimga qo&apos;shib qo&apos;ydim!
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Share Bottom Sheet */}
      <GlassBottomSheet isOpen={isShareOpen} onClose={() => setIsShareOpen(false)} title="Postni Ulashish">
        <div className="space-y-4 pt-2">
          <div className="grid grid-cols-2 gap-3">
            <a
              href={`https://t.me/share/url?url=${encodeURIComponent((typeof window !== 'undefined' ? window.location.origin : '') + `/posts/${post.id}`)}&text=${encodeURIComponent(post.title || post.content.substring(0, 50))}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2.5 p-3 rounded-2xl bg-[#0088cc]/20 hover:bg-[#0088cc]/30 text-[#0088cc] transition-colors font-display font-bold text-sm"
            >
              <Send className="w-5 h-5" />
              <span>Telegram orqali</span>
            </a>

            <button
              type="button"
              onClick={handleCopyLink}
              className="flex items-center gap-2.5 p-3 rounded-2xl bg-white/10 hover:bg-white/15 text-okj-text-primary transition-colors font-display font-bold text-sm"
            >
              {copiedLink ? <Check className="w-5 h-5 text-emerald-400" /> : <Copy className="w-5 h-5" />}
              <span>{copiedLink ? 'Nusxa olindi!' : 'Havola nusxalash'}</span>
            </button>
          </div>

          <GlassButton variant="secondary" className="w-full mt-2" onClick={() => setIsShareOpen(false)}>
            Yopish
          </GlassButton>
        </div>
      </GlassBottomSheet>
    </article>
  );
});
PostCard.displayName = 'PostCard';

