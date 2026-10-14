import React from 'react';
import { MapPin, Clock, Sparkles, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  isAdmin: boolean;
  userName?: string | null;
}

export const Header: React.FC<HeaderProps> = ({
  isAdmin,
  userName,
}) => {
  return (
    <header className="bg-nude-surface border-b border-nude-border px-3.5 py-2 sticky top-0 z-30 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-nude-accent flex items-center justify-center text-nude-primary font-bold shadow-inner">
            <Sparkles className="w-4 h-4 text-nude-primary" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-nude-text leading-tight">
              Sense Nail Studio
            </h1>
            <p className="text-[10px] text-nude-muted font-medium flex items-center gap-1">
              <span>Студія естетичного манікюру</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isAdmin ? (
            <span className="text-[10px] font-bold text-nude-primary bg-nude-accent/60 px-2.5 py-0.5 rounded-full border border-nude-primary/30">
              Адміністратор
            </span>
          ) : (
            userName && (
              <div className="text-[11px] font-medium text-nude-muted bg-nude-bg px-2.5 py-0.5 rounded-full border border-nude-border truncate max-w-[120px]">
                {userName}
              </div>
            )
          )}
        </div>
      </div>

      {/* Studio mini info row */}
      <div className="flex items-center justify-between text-[11px] text-nude-muted mt-1 px-1">
        <span>📍 вул. Січових Стрільців</span>
        <span>•</span>
        <span>🕒 09:00–20:00</span>
        <span>•</span>
        <span className="text-nude-green font-medium">✨ 100% стерильно</span>
      </div>
    </header>
  );
};
