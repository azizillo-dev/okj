'use client';

import React, { useState, useMemo } from 'react';
import clsx from 'clsx';
import { Flame, Calendar } from 'lucide-react';

export interface DailyContribution {
  date: string; // YYYY-MM-DD format
  pagesRead: number;
  xpEarned?: number;
  bookTitle?: string;
}

export interface ReadingHeatmapProps {
  contributions?: DailyContribution[];
  year?: number;
  className?: string;
}

/**
 * Responsive GitHub-style 365-day Reading Heatmap component with ARIA support and interactive tooltips.
 */
export const ReadingHeatmap: React.FC<ReadingHeatmapProps> = ({
  contributions = [],
  year = new Date().getFullYear(),
  className,
}) => {
  const [activeCell, setActiveCell] = useState<{ day: DailyContribution; x: number; y: number } | null>(null);

  // Generate full 365 days map
  const calendarDays = useMemo(() => {
    const daysMap = new Map<string, DailyContribution>();
    contributions.forEach((c) => daysMap.set(c.date, c));

    const startDate = new Date(year, 0, 1);
    const endDate = new Date(year, 11, 31);
    const allDays: DailyContribution[] = [];

    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      const dateStr = d.toISOString().split('T')[0];
      const existing = daysMap.get(dateStr);
      if (existing) {
        allDays.push(existing);
      } else {
        allDays.push({ date: dateStr, pagesRead: 0 });
      }
    }
    return allDays;
  }, [contributions, year]);

  // Group into 52/53 weeks of 7 days
  const weeks = useMemo(() => {
    const w: DailyContribution[][] = [];
    let currentWeek: DailyContribution[] = [];

    // Pad beginning of the first week if January 1 is not Monday
    const firstDayOfWeek = new Date(year, 0, 1).getDay(); // 0 is Sunday
    const padCount = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;
    for (let i = 0; i < padCount; i++) {
      currentWeek.push({ date: `pad-${i}`, pagesRead: -1 });
    }

    calendarDays.forEach((day) => {
      currentWeek.push(day);
      if (currentWeek.length === 7) {
        w.push(currentWeek);
        currentWeek = [];
      }
    });

    if (currentWeek.length > 0) {
      w.push(currentWeek);
    }
    return w;
  }, [calendarDays, year]);

  // Color intensity scale based on pages read
  const getCellColor = (pages: number): string => {
    if (pages < 0) return 'opacity-0 pointer-events-none';
    if (pages === 0) return 'bg-okj-surface/50 dark:bg-white/[0.04] border border-white/5';
    if (pages <= 15) return 'bg-indigo-500/30 border border-indigo-400/30';
    if (pages <= 40) return 'bg-okj-terracotta/60 border border-okj-terracotta/40';
    if (pages <= 80) return 'bg-okj-gold/80 text-okj-bg-deep font-bold border border-okj-gold shadow-sm';
    return 'bg-amber-400 text-black font-black shadow-[0_0_12px_rgba(251,191,36,0.6)] border border-amber-300 animate-pulse';
  };

  const totalPages = calendarDays.reduce((acc, curr) => acc + (curr.pagesRead > 0 ? curr.pagesRead : 0), 0);
  const activeDaysCount = calendarDays.filter((d) => d.pagesRead > 0).length;

  const months = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iun', 'Iul', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'];

  return (
    <div
      className={clsx(
        'p-6 rounded-3xl bg-okj-surface/60 dark:bg-[#1A253D]/80 backdrop-blur-2xl border border-white/15 shadow-2xl space-y-6 relative',
        className
      )}
      role="region"
      aria-label={`${year}-yil uchun o'qish xaritasi`}
    >
      {/* Header Summary */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-okj-gold font-display font-bold text-sm uppercase tracking-wider">
            <Flame className="w-4 h-4 fill-okj-gold" />
            <span>{year}-Yil O&apos;qish Faolligi</span>
          </div>
          <h3 className="font-display font-black text-2xl text-okj-text-primary mt-1">
            {totalPages.toLocaleString()} <span className="text-sm font-normal text-okj-text-secondary">sahifa o&apos;qildi</span>
          </h3>
        </div>

        <div className="flex items-center gap-6 text-xs text-okj-text-secondary bg-black/20 px-4 py-2 rounded-2xl border border-white/10">
          <div>
            Faol kunlar: <span className="font-bold text-okj-text-primary">{activeDaysCount} kun</span>
          </div>
          <div>
            O&apos;rtacha: <span className="font-bold text-okj-gold">{Math.round(totalPages / 365)} sahifa/kun</span>
          </div>
        </div>
      </div>

      {/* Heatmap Grid Container */}
      <div className="overflow-x-auto pb-4 no-scrollbar">
        <div className="min-w-[720px]">
          {/* Months Header */}
          <div className="grid grid-cols-12 text-[10px] font-mono text-okj-text-muted mb-2 px-6">
            {months.map((m) => (
              <span key={m}>{m}</span>
            ))}
          </div>

          <div className="flex gap-2 items-start">
            {/* Weekdays sidebar */}
            <div className="flex flex-col justify-between h-[104px] text-[10px] font-mono text-okj-text-muted pr-2 pt-1">
              <span>Du</span>
              <span>Ch</span>
              <span>Ju</span>
            </div>

            {/* Weeks Columns */}
            <div className="flex gap-1 flex-1">
              {weeks.map((week, wIdx) => (
                <div key={wIdx} className="flex flex-col gap-1">
                  {week.map((day, dIdx) => (
                    <button
                      key={`${wIdx}-${dIdx}`}
                      type="button"
                      disabled={day.pagesRead < 0}
                      onMouseEnter={(e) => {
                        if (day.pagesRead >= 0) {
                          const rect = e.currentTarget.getBoundingClientRect();
                          setActiveCell({ day, x: rect.left + rect.width / 2, y: rect.top });
                        }
                      }}
                      onMouseLeave={() => setActiveCell(null)}
                      onFocus={(e) => {
                        if (day.pagesRead >= 0) {
                          const rect = e.currentTarget.getBoundingClientRect();
                          setActiveCell({ day, x: rect.left + rect.width / 2, y: rect.top });
                        }
                      }}
                      onBlur={() => setActiveCell(null)}
                      className={clsx(
                        'w-3.5 h-3.5 rounded-sm transition-all duration-200 hover:scale-125 focus:outline-none focus:ring-2 focus:ring-okj-gold',
                        getCellColor(day.pagesRead)
                      )}
                      aria-label={`${day.date}: ${day.pagesRead > 0 ? `${day.pagesRead} sahifa` : 'o\'qilmagan'}`}
                    />
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Legend */}
      <div className="flex items-center justify-end gap-2 text-xs text-okj-text-muted pt-2 border-t border-white/10">
        <span>Kamroq</span>
        <span className="w-3 h-3 rounded-sm bg-okj-surface/50 border border-white/5" />
        <span className="w-3 h-3 rounded-sm bg-indigo-500/30" />
        <span className="w-3 h-3 rounded-sm bg-okj-terracotta/60" />
        <span className="w-3 h-3 rounded-sm bg-okj-gold" />
        <span className="w-3 h-3 rounded-sm bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.8)]" />
        <span>Ko&apos;proq</span>
      </div>

      {/* Floating Hover Tooltip */}
      {activeCell && (
        <div
          className="fixed z-50 px-3.5 py-2 rounded-xl bg-black/90 text-white text-xs backdrop-blur-md border border-white/20 shadow-2xl pointer-events-none -translate-x-1/2 -translate-y-full mb-2 animate-in fade-in zoom-in-95 duration-150"
          style={{ left: activeCell.x, top: activeCell.y - 8 }}
        >
          <div className="font-bold flex items-center gap-1.5 text-okj-gold">
            <Calendar className="w-3.5 h-3.5" />
            <span>{activeCell.day.date}</span>
          </div>
          <div className="mt-1">
            {activeCell.day.pagesRead > 0 ? (
              <span className="text-white font-medium">
                {activeCell.day.pagesRead} sahifa o&apos;qildi
                {activeCell.day.xpEarned ? ` (+${activeCell.day.xpEarned} XP)` : ''}
              </span>
            ) : (
              <span className="text-gray-400">Bu kunda kitob o&apos;qilmagan</span>
            )}
          </div>
          {activeCell.day.bookTitle && (
            <div className="text-[10px] text-gray-300 italic mt-0.5 truncate max-w-[180px]">
              &quot;{activeCell.day.bookTitle}&quot;
            </div>
          )}
        </div>
      )}
    </div>
  );
};
