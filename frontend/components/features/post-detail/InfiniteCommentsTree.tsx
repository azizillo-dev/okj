'use client';

import React, { useState } from 'react';
import { Heart, Reply, MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';
import { Comment } from '@/lib/api/types';
import { Avatar } from '@/components/ui';

interface InfiniteCommentsTreeProps {
  comments: Comment[];
  onSelectReply: (parent: { id: string; username: string }) => void;
}

export const InfiniteCommentsTree: React.FC<InfiniteCommentsTreeProps> = ({ comments, onSelectReply }) => {
  if (!comments || comments.length === 0) {
    return (
      <div className="p-8 text-center rounded-2xl bg-okj-surface/30 border border-okj-card-border/40 text-sm text-okj-text-muted">
        <MessageSquare className="w-8 h-8 text-okj-gold mx-auto mb-2 opacity-60" />
        <p>Hozircha izohlar yo&apos;q. Birinchi bo&apos;lib o&apos;z fikringizni bildiring!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4" role="feed" aria-label="Izohlar daraxti">
      {comments.map((comment) => (
        <CommentItem key={comment.id} comment={comment} onSelectReply={onSelectReply} />
      ))}
    </div>
  );
};

const CommentItem: React.FC<{
  comment: Comment;
  onSelectReply: (parent: { id: string; username: string }) => void;
  isReply?: boolean;
}> = ({ comment, onSelectReply, isReply = false }) => {
  const [likesCount, setLikesCount] = useState(comment.likes_count || 0);
  const [isLiked, setIsLiked] = useState(comment.is_liked_by_user || false);
  const [showReplies, setShowReplies] = useState(true);

  const handleLikeToggle = () => {
    setIsLiked((prev) => !prev);
    setLikesCount((prev) => (isLiked ? Math.max(0, prev - 1) : prev + 1));
  };

  const replies = comment.replies || [];

  return (
    <div className={`space-y-3 ${isReply ? 'ml-6 md:ml-10 border-l-2 border-okj-card-border pl-3 pt-1' : ''}`}>
      <div className="flex items-start gap-3 p-3.5 rounded-2xl bg-okj-surface/40 hover:bg-okj-surface/60 border border-okj-card-border/40 transition-colors">
        <Avatar user={comment.user} size="sm" />

        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex items-center justify-between gap-2">
            <span className="font-display font-bold text-xs text-okj-text-primary truncate">
              {comment.user.first_name} {comment.user.last_name || comment.user.username}
            </span>
            <span className="text-[10px] text-okj-text-muted font-mono">
              {new Date(comment.created_at).toLocaleDateString('uz-UZ', { month: 'short', day: 'numeric' })}
            </span>
          </div>

          <p className="text-xs text-okj-text-secondary leading-relaxed break-words">{comment.content}</p>

          <div className="flex items-center gap-4 pt-1 text-xs text-okj-text-muted">
            <button
              type="button"
              onClick={handleLikeToggle}
              className={`flex items-center gap-1 transition-colors ${isLiked ? 'text-rose-500 font-bold' : 'hover:text-okj-text-primary'}`}
              aria-label="Izohga like bosish"
            >
              <Heart className={`w-3.5 h-3.5 ${isLiked ? 'fill-rose-500' : ''}`} />
              <span>{likesCount}</span>
            </button>

            <button
              type="button"
              onClick={() => onSelectReply({ id: comment.id, username: comment.user.username })}
              className="flex items-center gap-1 hover:text-okj-gold transition-colors"
              aria-label="Izohga javob yozish"
            >
              <Reply className="w-3.5 h-3.5" />
              <span>Javob yozish</span>
            </button>

            {replies.length > 0 && (
              <button
                type="button"
                onClick={() => setShowReplies((prev) => !prev)}
                className="flex items-center gap-1 text-okj-gold hover:underline"
              >
                {showReplies ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                <span>{replies.length} ta javob</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Nested Replies Tree */}
      {showReplies && replies.length > 0 && (
        <div className="space-y-2">
          {replies.map((reply) => (
            <CommentItem key={reply.id} comment={reply} onSelectReply={onSelectReply} isReply />
          ))}
        </div>
      )}
    </div>
  );
};
