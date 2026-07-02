'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import clsx from 'clsx';
import { Heart, MessageCircle, Share2, Quote, Tag, Gift, Repeat } from 'lucide-react';
import { Post } from '@/lib/api/types';
import { Avatar } from './Avatar';
import { postsApi } from '@/lib/api/posts';

interface PostCardProps {
  post: Post;
  onLikeToggle?: (postId: string, newLiked: boolean, newCount: number) => void;
}

export const PostCard: React.FC<PostCardProps> = ({ post, onLikeToggle }) => {
  const [isLiked, setIsLiked] = useState(post.is_liked_by_user || false);
  const [likesCount, setLikesCount] = useState(post.likes_count || 0);
  const [isLiking, setIsLiking] = useState(false);

  const handleLike = async () => {
    if (isLiking) return;
    const prevLiked = isLiked;
    const prevCount = likesCount;

    const nextLiked = !prevLiked;
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

  const isQuote = post.post_type === 'QUOTE';
  const isExchangeOrSell = post.post_type === 'EXCHANGE' || post.post_type === 'SELL';
  const isGift = post.post_type === 'GIFT';

  const typeBadge = {
    QUOTE: { label: 'Iqtibos', icon: Quote, color: 'text-okj-gold bg-okj-gold/10' },
    REVIEW: { label: 'Taqriz', icon: MessageCircle, color: 'text-indigo-400 bg-indigo-500/10' },
    SHOWCASE: { label: 'Ko\'rgazma', icon: Share2, color: 'text-emerald-400 bg-emerald-500/10' },
    EXCHANGE: { label: 'Almashish', icon: Repeat, color: 'text-okj-terracotta bg-okj-terracotta/10' },
    GIFT: { label: 'Sovg\'a', icon: Gift, color: 'text-rose-400 bg-rose-500/10' },
    SELL: { label: 'Sotuvda', icon: Tag, color: 'text-okj-terracotta bg-okj-terracotta/10' },
  }[post.post_type] || { label: post.post_type, icon: MessageCircle, color: 'text-okj-text-secondary bg-okj-surface' };

  const IconComponent = typeBadge.icon;

  return (
    <article
      className={clsx(
        'rounded-2xl border transition-colors duration-200 overflow-hidden',
        isQuote
          ? 'bg-okj-parchment text-okj-parchment-text border-okj-gold/30 shadow-md'
          : 'bg-okj-card text-okj-text-primary border-okj-card-border',
        isExchangeOrSell && !isQuote && 'border-l-4 border-l-okj-terracotta'
      )}
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

      {/* Content Body */}
      <div className="p-4">
        {post.title && (
          <h3 className={clsx('font-display font-bold text-base mb-2', isQuote ? 'text-okj-parchment-text' : 'text-okj-text-primary')}>
            {post.title}
          </h3>
        )}

        {isQuote ? (
          <blockquote className="font-display italic text-lg leading-relaxed border-l-2 border-okj-gold/60 pl-4 py-1 my-2">
            "{post.content}"
          </blockquote>
        ) : (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{post.content}</p>
        )}

        {/* Exchange/Sell Price info */}
        {isExchangeOrSell && post.price && (
          <div className="mt-3 inline-block px-3 py-1 rounded-lg bg-okj-terracotta/15 text-okj-terracotta font-bold text-sm">
            Narxi: {post.price.toLocaleString()} UZS
          </div>
        )}
      </div>

      {/* Media Attachments */}
      {post.media && post.media.length > 0 && (
        <div className="relative w-full aspect-video bg-okj-surface overflow-hidden">
          <Image
            src={post.media[0].file_url}
            alt="Post media"
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 640px"
          />
        </div>
      )}

      {/* Footer / Actions */}
      <div
        className={clsx(
          'px-4 py-3 flex items-center justify-between text-xs border-t',
          isQuote ? 'border-okj-gold/20 text-okj-parchment-text/80' : 'border-okj-card-border/40 text-okj-text-secondary'
        )}
      >
        <button
          onClick={handleLike}
          className={clsx(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-colors active:scale-95',
            isLiked
              ? 'text-rose-500 bg-rose-500/10 font-bold'
              : isQuote
              ? 'hover:bg-okj-parchment-text/10'
              : 'hover:bg-okj-surface'
          )}
        >
          <Heart className={clsx('w-4 h-4', isLiked && 'fill-rose-500')} />
          <span>{likesCount}</span>
        </button>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 px-3 py-1.5">
            <MessageCircle className="w-4 h-4" />
            <span>{post.comments_count || 0}</span>
          </div>
        </div>
      </div>
    </article>
  );
};
