'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import confetti from 'canvas-confetti';
import { Trophy, Sparkles, Loader2, Gift } from 'lucide-react';
import { GlassModal, GlassButton } from '@/components/ui/glass';

export interface SpinWheelReward {
  id: string;
  label: string;
  subLabel?: string;
  color: string;
  textColor?: string;
}

export interface DailySpinWheelProps {
  isOpen: boolean;
  onClose: () => void;
  sectors?: SpinWheelReward[];
  /**
   * Callback triggered when user clicks Spin.
   * Should return a Promise resolving to the index (0 to 5) determined by the backend API.
   */
  onRequestSpin: () => Promise<number>;
  onSpinCompleted?: (reward: SpinWheelReward) => void;
}

const DEFAULT_SECTORS: SpinWheelReward[] = [
  { id: '1', label: '+50 XP', subLabel: 'Kunlik bonus', color: '#D3A85C', textColor: '#17233D' },
  { id: '2', label: '+100 XP', subLabel: 'Super bonus', color: '#4F46E5', textColor: '#FFFFFF' },
  { id: '3', label: '🧊 Muzlatkich', subLabel: 'Streak Freeze', color: '#06B6D4', textColor: '#FFFFFF' },
  { id: '4', label: '👑 +200 XP', subLabel: 'JACKPOT', color: '#E11D48', textColor: '#FFFFFF' },
  { id: '5', label: '🏷️ Chek', subLabel: 'Bepul Almashish', color: '#10B981', textColor: '#FFFFFF' },
  { id: '6', label: '+30 XP', subLabel: 'Kichik mukofot', color: '#C1694A', textColor: '#FFFFFF' },
];

/**
 * Duolingo-style Daily Spin Wheel component with Framer Motion deceleration physics
 * and backend-driven cheating-proof stopping target. Fires Canvas Confetti on win.
 */
export const DailySpinWheel: React.FC<DailySpinWheelProps> = ({
  isOpen,
  onClose,
  sectors = DEFAULT_SECTORS,
  onRequestSpin,
  onSpinCompleted,
}) => {
  const [isSpinning, setIsSpinning] = useState(false);
  const [rotation, setRotation] = useState(0);
  const [wonReward, setWonReward] = useState<SpinWheelReward | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const sectorAngle = 360 / sectors.length;

  const handleSpin = async () => {
    if (isSpinning || wonReward) return;
    setIsSpinning(true);
    setErrorMsg(null);

    try {
      // Step 1: Query backend API for stopping index
      const targetIndex = await onRequestSpin();

      if (targetIndex < 0 || targetIndex >= sectors.length) {
        throw new Error('Backenddan noto\'g\'ri yutuq indeksi keldi.');
      }

      // Step 2: Calculate target rotation degree in CSS
      // To land on targetIndex pointer at 0 deg (top), wheel needs to spin at least 5 full rotations (1800 deg)
      const baseSpins = 360 * 6;
      // Center of target sector relative to 0 deg
      const targetOffset = 360 - (targetIndex * sectorAngle + sectorAngle / 2);
      const nextRotation = rotation + baseSpins + (targetOffset - (rotation % 360));

      setRotation(nextRotation);

      // Step 3: Wait for animation to finish (approx 4.5 seconds)
      setTimeout(() => {
        setIsSpinning(false);
        const reward = sectors[targetIndex];
        setWonReward(reward);
        onSpinCompleted?.(reward);

        // Fire Canvas Confetti celebration
        if (typeof window !== 'undefined') {
          confetti({
            particleCount: 120,
            spread: 80,
            origin: { y: 0.6 },
            colors: ['#D3A85C', '#4F46E5', '#E11D48', '#10B981'],
          });
        }
      }, 4500);
    } catch (err: any) {
      setIsSpinning(false);
      setErrorMsg(err.message || 'G\'ildirakni aylantirishda xatolik yuz berdi.');
    }
  };

  return (
    <GlassModal isOpen={isOpen} onClose={onClose} maxWidth="md">
      <div className="flex flex-col items-center text-center space-y-6 py-2">
        {/* Header */}
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-okj-gold/20 text-okj-gold text-xs font-display font-bold uppercase tracking-widest">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Kunlik Omad G&apos;ildiragi</span>
          </div>
          <h2 className="font-display font-black text-2xl text-okj-text-primary">
            {wonReward ? 'Tabriklaymiz!' : 'G&apos;ildirakni Aylantiring!'}
          </h2>
          <p className="text-xs text-okj-text-secondary max-w-xs mx-auto">
            {wonReward
              ? `Siz "${wonReward.label}" mukofotini yutib oldingiz va u pasportingizga qo'shildi.`
              : 'Har kuni bir marta bepul aylantirib, o\'qish seriyangiz va XP ballaringizni ko\'taring.'}
          </p>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-xl bg-rose-500/20 text-rose-300 text-xs font-medium w-full">
            {errorMsg}
          </div>
        )}

        {/* Wheel Assembly */}
        <div className="relative w-64 h-64 sm:w-72 sm:h-72 my-4 flex items-center justify-center select-none">
          {/* Top pointer arrow */}
          <div className="absolute -top-3 z-20 w-8 h-8 rounded-full bg-okj-gold text-okj-bg-deep flex items-center justify-center shadow-xl border-2 border-white">
            <div className="w-0 h-0 border-x-6 border-x-transparent border-t-8 border-t-okj-gold absolute -bottom-2" />
          </div>

          {/* Rotating Wheel Circle */}
          <motion.div
            className="w-full h-full rounded-full border-4 border-okj-gold/60 shadow-[0_0_40px_rgba(211,168,92,0.25)] relative overflow-hidden"
            animate={{ rotate: rotation }}
            transition={{ duration: 4.5, ease: [0.15, 0.9, 0.25, 1] }} // Cubic bezier smooth deceleration physics
          >
            {sectors.map((sec, idx) => {
              const startAngle = idx * sectorAngle;
              return (
                <div
                  key={sec.id}
                  className="absolute inset-0 flex flex-col items-center pt-4 font-display font-bold text-xs"
                  style={{
                    transform: `rotate(${startAngle + sectorAngle / 2}deg)`,
                    transformOrigin: 'center center',
                    clipPath: 'polygon(50% 50%, 0 0, 100% 0)',
                    backgroundColor: sec.color,
                    color: sec.textColor || '#FFFFFF',
                  }}
                >
                  <span className="text-sm font-black mt-2">{sec.label}</span>
                  {sec.subLabel && <span className="text-[9px] opacity-90">{sec.subLabel}</span>}
                </div>
              );
            })}
          </motion.div>

          {/* Center Hub Cap */}
          <div className="absolute z-10 w-16 h-16 rounded-full bg-okj-surface border-4 border-okj-gold shadow-2xl flex items-center justify-center">
            <Gift className="w-7 h-7 text-okj-gold animate-bounce" />
          </div>
        </div>

        {/* Action Controls */}
        <div className="w-full pt-2">
          {!wonReward ? (
            <GlassButton
              variant="gold"
              size="lg"
              className="w-full"
              onClick={handleSpin}
              disabled={isSpinning}
            >
              {isSpinning ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>G&apos;ildirak aylanmoqda...</span>
                </>
              ) : (
                <>
                  <Trophy className="w-5 h-5" />
                  <span>OMADNI SINOVdan o&apos;tkazish</span>
                </>
              )}
            </GlassButton>
          ) : (
            <GlassButton variant="secondary" size="lg" className="w-full font-bold" onClick={onClose}>
              Mukofotni Olish va Davom etish
            </GlassButton>
          )}
        </div>
      </div>
    </GlassModal>
  );
};
