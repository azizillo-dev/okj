'use client';

import React from 'react';
import Image from 'next/image';
import clsx from 'clsx';
import { UserProfile } from '@/lib/api/types';

interface AvatarProps {
  user: Partial<UserProfile>;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const PALETTE = [
  'bg-amber-600',
  'bg-indigo-600',
  'bg-emerald-600',
  'bg-purple-600',
  'bg-rose-600',
  'bg-cyan-600',
];

const getHashColor = (idOrName: string = 'okj'): string => {
  let hash = 0;
  for (let i = 0; i < idOrName.length; i++) {
    hash = idOrName.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % PALETTE.length;
  return PALETTE[index];
};

export const Avatar: React.FC<AvatarProps> = React.memo(({ user, size = 'md', className }) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-11 h-11 text-base',
    lg: 'w-16 h-16 text-xl',
  }[size];

  const initials = `${user.first_name?.[0] || ''}${user.last_name?.[0] || user.username?.[0] || 'U'}`.toUpperCase();
  const bgColorClass = getHashColor(user.id || user.username);

  return (
    <div
      className={clsx(
        'relative inline-flex items-center justify-center rounded-full overflow-hidden shrink-0 font-display font-bold text-white shadow-inner',
        sizeClasses,
        !user.avatar && bgColorClass,
        className
      )}
    >
      {user.avatar ? (
        <Image
          src={user.avatar}
          alt={user.username || 'Kitobxon'}
          fill
          className="object-cover"
          sizes="(max-width: 768px) 64px, 64px"
        />
      ) : (
        <span>{initials}</span>
      )}
    </div>
  );
});
Avatar.displayName = 'Avatar';

