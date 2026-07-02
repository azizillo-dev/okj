'use client';

import React, { useState } from 'react';
import clsx from 'clsx';
import { motion } from 'framer-motion';
import { UserCheck, UserPlus, Loader2 } from 'lucide-react';
import { passportApi } from '@/lib/api/passport';

interface FollowButtonProps {
  userId: string;
  initialFollowing?: boolean;
  className?: string;
  onFollowChange?: (following: boolean) => void;
}

export const FollowButton: React.FC<FollowButtonProps> = ({
  userId,
  initialFollowing = false,
  className,
  onFollowChange,
}) => {
  const [isFollowing, setIsFollowing] = useState(initialFollowing);
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (isLoading) return;

    const previousState = isFollowing;
    const nextState = !previousState;

    // Optimistic UI Update
    setIsFollowing(nextState);
    onFollowChange?.(nextState);
    setIsLoading(true);

    try {
      const response = await passportApi.followUser(userId);
      setIsFollowing(response.following);
      onFollowChange?.(response.following);
    } catch {
      // Revert state if API request failed
      setIsFollowing(previousState);
      onFollowChange?.(previousState);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.94 }}
      transition={{ type: 'spring', stiffness: 400, damping: 20 }}
      onClick={handleClick}
      disabled={isLoading}
      className={clsx(
        'inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl font-display font-medium text-sm transition-colors disabled:opacity-70 disabled:cursor-not-allowed',
        isFollowing
          ? 'bg-okj-surface text-okj-text-primary border border-okj-card-border hover:border-rose-500/50 hover:text-rose-400'
          : 'bg-okj-gold text-okj-bg-deep font-bold hover:bg-okj-gold/90 shadow-md shadow-okj-gold/20',
        className
      )}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : isFollowing ? (
        <>
          <UserCheck className="w-4 h-4" />
          <span>Obunadasiz</span>
        </>
      ) : (
        <>
          <UserPlus className="w-4 h-4" />
          <span>Obuna bo&apos;lish</span>
        </>
      )}
    </motion.button>
  );
};

