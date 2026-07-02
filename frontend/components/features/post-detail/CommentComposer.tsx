'use client';

import React, { useState } from 'react';
import { Smile, Send, X, AtSign } from 'lucide-react';
import { GlassCard } from '@/components/ui/glass';

const EMOJI_LIST = ['❤️', '🔥', '📚', '✨', '💡', '👏', '🎯', '⭐', '🚀', '💎', '✍️', '⚡'];

interface CommentComposerProps {
  replyingTo?: { id: string; username: string } | null;
  onCancelReply?: () => void;
  onSubmitComment: (content: string, parentId?: string) => Promise<void>;
}

export const CommentComposer: React.FC<CommentComposerProps> = ({
  replyingTo,
  onCancelReply,
  onSubmitComment,
}) => {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showEmojis, setShowEmojis] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const finalContent = replyingTo ? `@${replyingTo.username} ${content}` : content;
      await onSubmitComment(finalContent, replyingTo?.id);
      setContent('');
      if (onCancelReply) onCancelReply();
    } finally {
      setIsSubmitting(false);
    }
  };

  const insertEmoji = (emoji: string) => {
    setContent((prev) => prev + emoji);
    setShowEmojis(false);
  };

  return (
    <GlassCard variant="subtle" className="p-4 space-y-3 relative">
      {/* Replying indicator banner */}
      {replyingTo && (
        <div className="flex items-center justify-between px-3 py-1.5 rounded-xl bg-okj-gold/15 border border-okj-gold/30 text-xs">
          <div className="flex items-center gap-1.5 font-display font-bold text-okj-gold">
            <AtSign className="w-3.5 h-3.5" />
            <span>@{replyingTo.username} ga javob yozilmoqda</span>
          </div>
          <button
            type="button"
            onClick={onCancelReply}
            className="p-1 rounded-lg hover:bg-okj-gold/20 text-okj-gold transition-colors"
            aria-label="Javobni bekor qilish"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-2">
        <div className="relative">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={replyingTo ? `@${replyingTo.username} ga javobingiz...` : "Fikringizni qoldiring... (@eslatib o'tish mumkin)"}
            rows={2}
            disabled={isSubmitting}
            className="w-full rounded-2xl bg-okj-bg-deep/80 border border-okj-card-border/60 p-3.5 pr-12 text-sm text-okj-text-primary placeholder:text-okj-text-muted focus:outline-none focus:border-okj-gold transition-colors resize-none"
          />

          {/* Emoji Toggle Button */}
          <button
            type="button"
            onClick={() => setShowEmojis((prev) => !prev)}
            className="absolute right-3 bottom-3.5 p-1.5 rounded-xl hover:bg-white/10 text-okj-text-secondary transition-colors"
            aria-label="Emojilar paneli"
          >
            <Smile className="w-5 h-5" />
          </button>
        </div>

        {/* Emoji Popover Grid */}
        {showEmojis && (
          <div className="p-2.5 rounded-2xl bg-okj-surface border border-okj-card-border grid grid-cols-6 gap-2 animate-fadeIn">
            {EMOJI_LIST.map((em) => (
              <button
                key={em}
                type="button"
                onClick={() => insertEmoji(em)}
                className="p-1.5 text-lg hover:bg-white/10 rounded-xl transition-transform active:scale-125"
              >
                {em}
              </button>
            ))}
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!content.trim() || isSubmitting}
            className="flex items-center gap-2 px-5 py-2 rounded-xl bg-okj-gold text-okj-bg-deep font-display font-bold text-xs hover:bg-okj-gold-light transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none shadow-lg shadow-okj-gold/20"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSubmitting ? 'Yuborilmoqda...' : 'Yuborish'}</span>
          </button>
        </div>
      </form>
    </GlassCard>
  );
};
