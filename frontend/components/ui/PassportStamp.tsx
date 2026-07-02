'use client';

import React from 'react';
import clsx from 'clsx';
import { Lock } from 'lucide-react';

interface PassportStampProps {
  icon: string;
  label: string;
  locked?: boolean;
}

export const PassportStamp: React.FC<PassportStampProps> = React.memo(({ icon, label, locked = false }) => {
  return (
    <div
      className={clsx(
        'group flex flex-col items-center justify-center p-3 rounded-full w-24 h-24 border-2 transition-transform duration-300 select-none text-center',
        locked
          ? 'border-dashed border-okj-card-border bg-okj-surface/50 opacity-50 cursor-not-allowed'
          : 'border-dashed border-okj-gold bg-okj-card text-okj-gold hover:scale-105 shadow-[0_0_15px_rgba(211,168,92,0.15)]'
      )}
    >
      <div className="text-2xl mb-1 flex items-center justify-center">
        {locked ? <Lock className="w-6 h-6 text-okj-text-muted" /> : <span>{icon}</span>}
      </div>
      <span
        className={clsx(
          'text-[10px] font-display uppercase tracking-wider leading-tight line-clamp-2 px-1',
          locked ? 'text-okj-text-muted' : 'text-okj-text-primary'
        )}
      >
        {label}
      </span>
    </div>
  );
});
PassportStamp.displayName = 'PassportStamp';

