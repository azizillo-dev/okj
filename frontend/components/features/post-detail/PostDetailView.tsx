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
  Bookmark,
  Quote,
  Repeat,
  Gift,
  Tag,
  BookOpen,
  ArrowLeft,
  Copy,
  Send,
  Check,
  Percent,
} from 'lucide-react';
import { Post, Comment } from '@/lib/api/types';
import { postsApi } from '@/lib/api/posts';
import { Avatar, FollowButton } from '@/components/ui';
import { GlassCard, GlassBottomSheet, GlassButton } from '@/components/ui/glass';
import { FullscreenMediaViewer } from './FullscreenMediaViewer';
import { CommentComposer } from './CommentComposer';
import { InfiniteCommentsTree } from './InfiniteCommentsTree';
import { PostActionsMenu } from './PostActionsMenu';
import { RelatedContentWidget } from './RelatedContentWidget';

interface PostDetailViewProps {
  post: Post;
  initialComments: Comment[];
  currentUserId?: string;
}

export const PostDetailView: React.FC<PostDetailViewProps> = ({ post, initialComments, currentUserId = 'u-10492' }) => {
  const [isLiked, setIsLiked] = useState(post.is_liked_by_user || false);
  const [likesCount, setLikesCount] = useState(post.likes_count || 0);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [showHeartAnim, setShowHeartAnim] = useState(false);
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  const [viewerOpen, setViewerOpen] = useState(false);
  const [viewerIndex, setViewerIndex] = useState(0);

  const [comments, setComments] = useState<Comment[]>(initialComments || []);
  const [replyingTo, setReplyingTo] = useState<{ id: string; username: string } | null>(null);

  // Interactive reading progress simulation (if user is reading this book)
  const [readingProgress, setReadingProgress] = useState<number>(post.quote_page ? Math.min(100, Math.floor((post.quote_page / 350) * 100)) : 42);

  const lastTapRef = useRef<number>(0);
  const isAuthor = post.user.id === currentUserId || post.user.okj_id === currentUserId;

  const handleLike = async (forcedValue?: boolean) => {
    const prevLiked = isLiked;
    const prevCount = likesCount;
    const nextLiked = forcedValue !== undefined ? forcedValue : !prevLiked;
    if (nextLiked === prevLiked) return;

    setIsLiked(nextLiked);
    setLikesCount(nextLiked ? prevCount + 1 : Math.max(0, prevCount - 1));

    try {
      const res = await postsApi.likePost(post.id);
      setIsLiked(res.liked);
      setLikesCount(res.likes_count);
    } catch {
      setIsLiked(prevLiked);
      setLikesCount(prevCount);
    }
  };

  const handleDoubleTap = () => {
    const now = Date.now();
    if (now - lastTapRef.current < 300) {
      setShowHeartAnim(true);
      setTimeout(() => setShowHeartAnim(false), 800);
      if (!isLiked) handleLike(true);
    }
    lastTapRef.current = now;
  };

  const handleAddComment = async (content: string, parentId?: string) => {
    try {
      const newComment = await postsApi.addComment(post.id, content, parentId);
      if (parentId) {
        // Add nested reply to parent thread
        setComments((prev) =>
          prev.map((c) => {
            if (c.id === parentId) {
              return { ...c, replies: [...(c.replies || []), newComment] };
            }
            return c;
          })
        );
      } else {
        setComments((prev) => [newComment, ...prev]);
      }
    } catch {
      // Optimistic fallback addition
      const optimisticComment: Comment = {
        id: `local-${Date.now()}`,
        post_id: post.id,
        parent_id: parentId || null,
        user: {
          id: currentUserId,
          username: 'alisher_rustamov',
          first_name: 'Alisher',
          last_name: 'Rustamov',
          okj_id: 'OKJ-10492',
          total_xp: 1450,
        },
        content,
        likes_count: 0,
        created_at: new Date().toISOString(),
        replies: [],
      };

      if (parentId) {
        setComments((prev) =>
          prev.map((c) => (c.id === parentId ? { ...c, replies: [...(c.replies || []), optimisticComment] } : c))
        );
      } else {
        setComments((prev) => [optimisticComment, ...prev]);
      }
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard?.writeText(typeof window !== 'undefined' ? window.location.href : '');
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const isQuote = post.post_type === 'QUOTE';
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
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      {/* Top Navigation Back */}
      <div className="flex items-center justify-between">
        <Link
          href="/feed"
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-medium text-okj-text-secondary hover:text-okj-text-primary transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Lentaga Qaytish</span>
        </Link>

        <PostActionsMenu post={post} isAuthor={isAuthor} />
      </div>

      {/* Main Post Container Card */}
      <GlassCard
        variant={isQuote ? 'prominent' : 'default'}
        className={clsx('p-6 md:p-8 space-y-6 relative select-none', isQuote && 'bg-okj-parchment/10 border-okj-gold/40')}
      >
        {/* Author Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <Link href={`/u/${post.user.okj_id || post.user.id}`}>
              <Avatar user={post.user} size="md" className="border-2 border-okj-gold/60" />
            </Link>
            <div>
              <Link href={`/u/${post.user.okj_id || post.user.id}`} className="hover:underline">
                <h2 className="font-display font-bold text-base text-okj-text-primary">
                  {post.user.first_name} {post.user.last_name || post.user.username}
                </h2>
              </Link>
              <p className="text-xs text-okj-text-secondary font-mono">
                {post.user.okj_id ? `${post.user.okj_id} • ` : ''}
                {new Date(post.created_at).toLocaleDateString('uz-UZ', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 self-start sm:self-center">
            <span className={clsx('inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold', typeBadge.color)}>
              <IconComponent className="w-4 h-4" />
              <span>{typeBadge.label}</span>
            </span>

            {!isAuthor && <FollowButton userId={post.user.id} />}
          </div>
        </div>

        {/* Book Badge & Reading Progress Bar */}
        {post.book && (
          <div className="p-4 rounded-2xl bg-okj-surface/60 border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <BookOpen className="w-5 h-5 text-okj-gold shrink-0" />
                <div>
                  <span className="text-xs text-okj-text-muted block">Kitob haqida:</span>
                  <Link href={`/books/${post.book.slug}`} className="font-display font-bold text-sm text-okj-text-primary hover:text-okj-gold">
                    {post.book.title}
                  </Link>
                </div>
              </div>
              {post.quote_page && (
                <span className="px-3 py-1 rounded-xl bg-okj-gold/20 text-okj-gold font-mono text-xs font-bold">
                  {post.quote_page}-sahifa
                </span>
              )}
            </div>

            {/* Reading Progress Indicator */}
            <div className="pt-2 border-t border-white/5 space-y-1.5">
              <div className="flex justify-between text-[11px] font-mono text-okj-text-secondary">
                <span>Kitobni o&apos;qish jarayoningiz:</span>
                <span className="text-okj-gold font-bold flex items-center gap-0.5">
                  <span>{readingProgress}%</span>
                  <Percent className="w-3 h-3" />
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={readingProgress}
                onChange={(e) => setReadingProgress(Number(e.target.value))}
                className="w-full h-1.5 bg-okj-bg-deep rounded-lg appearance-none cursor-pointer accent-okj-gold"
                aria-label="O'qish jarayoni slayderi"
              />
            </div>
          </div>
        )}

        {/* Interactive Content Body */}
        <div className="relative cursor-pointer py-2" onClick={handleDoubleTap}>
          {post.title && <h1 className="font-display font-black text-xl md:text-2xl text-okj-text-primary mb-3">{post.title}</h1>}

          {isQuote ? (
            <blockquote className="font-display italic text-xl md:text-2xl leading-relaxed border-l-4 border-okj-gold pl-6 py-2 my-2 text-okj-text-primary">
              &quot;{post.content}&quot;
            </blockquote>
          ) : (
            <p className="text-base leading-relaxed text-okj-text-primary whitespace-pre-wrap">{post.content}</p>
          )}

          {post.price && (
            <div className="mt-4 inline-block px-4 py-2 rounded-xl bg-okj-terracotta/20 border border-okj-terracotta/40 text-okj-terracotta font-display font-bold text-base">
              Narxi: {post.price.toLocaleString()} UZS
            </div>
          )}

          {/* Double Tap Heart Burst Animation */}
          <AnimatePresence>
            {showHeartAnim && (
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1.8, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
                transition={{ duration: 0.35, type: 'spring' }}
                className="absolute inset-0 flex items-center justify-center pointer-events-none z-30"
              >
                <Heart className="w-24 h-24 fill-rose-500 text-rose-500 drop-shadow-2xl" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Media Attachments */}
        {post.media && post.media.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            {post.media.map((med, idx) => (
              <div
                key={med.id}
                onClick={() => {
                  setViewerIndex(idx);
                  setViewerOpen(true);
                }}
                className="relative aspect-video rounded-2xl overflow-hidden border border-white/15 cursor-pointer group shadow-lg"
              >
                <Image src={med.file_url} alt="Media attachment" fill className="object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <span className="px-3 py-1.5 rounded-full bg-black/60 text-white text-xs font-display font-bold backdrop-blur-md">
                    To&apos;liq ekranda ko&apos;rish
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action Bar */}
        <div className="pt-4 border-t border-white/10 flex items-center justify-between text-sm">
          <div className="flex items-center gap-6">
            <button
              type="button"
              onClick={() => handleLike()}
              className={clsx(
                'flex items-center gap-2 px-4 py-2 rounded-full transition-all active:scale-95',
                isLiked ? 'bg-rose-500/20 text-rose-500 font-bold' : 'hover:bg-white/10 text-okj-text-secondary'
              )}
            >
              <Heart className={clsx('w-5 h-5', isLiked && 'fill-rose-500')} />
              <span>{likesCount}</span>
            </button>

            <div className="flex items-center gap-2 px-4 py-2 text-okj-text-secondary font-medium">
              <MessageCircle className="w-5 h-5" />
              <span>{comments.length} ta izoh</span>
            </div>

            <button
              type="button"
              onClick={() => setIsShareOpen(true)}
              className="p-2.5 rounded-full hover:bg-white/10 text-okj-text-secondary transition-colors"
              aria-label="Ulashish"
            >
              <Share2 className="w-5 h-5" />
            </button>
          </div>

          <button
            type="button"
            onClick={() => setIsBookmarked((prev) => !prev)}
            className={clsx(
              'p-2.5 rounded-full transition-all active:scale-95',
              isBookmarked ? 'text-okj-gold bg-okj-gold/15' : 'hover:bg-white/10 text-okj-text-secondary'
            )}
            aria-label="Saqlab qo'yish"
          >
            <Bookmark className={clsx('w-5 h-5', isBookmarked && 'fill-okj-gold')} />
          </button>
        </div>
      </GlassCard>

      {/* Comment Composer */}
      <div className="space-y-4">
        <h3 className="font-display font-bold text-lg text-okj-text-primary flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-okj-gold" />
          <span>Fikrlar va Muhokamalar ({comments.length})</span>
        </h3>

        <CommentComposer
          replyingTo={replyingTo}
          onCancelReply={() => setReplyingTo(null)}
          onSubmitComment={handleAddComment}
        />
      </div>

      {/* Infinite Comments Tree */}
      <InfiniteCommentsTree comments={comments} onSelectReply={(parent) => setReplyingTo(parent)} />

      {/* Related Content Showcase */}
      <RelatedContentWidget currentBook={post.book} relatedPosts={[]} />

      {/* Fullscreen Media Viewer Modal */}
      {post.media && post.media.length > 0 && (
        <FullscreenMediaViewer
          media={post.media}
          initialIndex={viewerIndex}
          isOpen={viewerOpen}
          onClose={() => setViewerOpen(false)}
        />
      )}

      {/* Share Bottom Sheet */}
      <GlassBottomSheet isOpen={isShareOpen} onClose={() => setIsShareOpen(false)} title="Postni Ulashish">
        <div className="space-y-4 pt-2">
          <div className="grid grid-cols-2 gap-3">
            <a
              href={`https://t.me/share/url?url=${encodeURIComponent((typeof window !== 'undefined' ? window.location.href : ''))}&text=${encodeURIComponent(post.title || post.content.substring(0, 50))}`}
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
    </div>
  );
};
