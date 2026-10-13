import React from 'react';
import { MapPin, Clock, Sparkles, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  isAdmin: boolean;
  activeTab: 'client' | 'admin';
  onTabChange: (tab: 'client' | 'admin') => void;
  userName?: string | null;
}

export const Header: React.FC<HeaderProps> = ({
  isAdmin,
  activeTab,
  onTabChange,
  userName,
}) => {
  return (
    <header className="bg-nude-surface border-b border-nude-border px-4 py-3 sticky top-0 z-30 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-nude-accent flex items-center justify-center text-nude-primary font-bold shadow-inner">
            <Sparkles className="w-5 h-5 text-nude-primary" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-nude-text leading-tight">
              Sense Nail Studio
            </h1>
            <p className="text-xs text-nude-muted font-medium flex items-center gap-1">
              <span>Студія естетичного манікюру</span>
            </p>
          </div>
        </div>

        {userName && (
          <div className="text-xs font-medium text-nude-muted bg-nude-bg px-2.5 py-1 rounded-full border border-nude-border">
            {userName}
          </div>
        )}
      </div>

      {/* Studio mini info badges */}
      <div className="flex items-center gap-2 mt-2.5 text-[11px] text-nude-muted">
        <span className="flex items-center gap-1 bg-nude-bg px-2 py-0.5 rounded-md border border-nude-border/60">
          <MapPin className="w-3 h-3 text-nude-primary" />
          вул. Січових Стрільців
        </span>
        <span className="flex items-center gap-1 bg-nude-bg px-2 py-0.5 rounded-md border border-nude-border/60">
          <Clock className="w-3 h-3 text-nude-primary" />
          09:00 – 20:00
        </span>
        <span className="flex items-center gap-1 bg-nude-greenLight text-nude-green px-2 py-0.5 rounded-md font-medium">
          <ShieldCheck className="w-3 h-3" />
          100% стерильно
        </span>
      </div>

      {/* Admin Switcher */}
      {isAdmin && (
        <div className="mt-3 pt-2.5 border-t border-nude-border/80">
          <div className="bg-nude-bg p-1 rounded-xl flex items-center gap-1 border border-nude-border">
            <button
              type="button"
              onClick={() => onTabChange('client')}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center justify-center gap-1.5 ${
                activeTab === 'client'
                  ? 'bg-nude-surface text-nude-text shadow-sm border border-nude-border'
                  : 'text-nude-muted hover:text-nude-text'
              }`}
            >
              💅 Клієнтська аппка
            </button>
            <button
              type="button"
              onClick={() => onTabChange('admin')}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center justify-center gap-1.5 ${
                activeTab === 'admin'
                  ? 'bg-nude-primary text-white shadow-sm'
                  : 'text-nude-muted hover:text-nude-text'
              }`}
            >
              ⚙️ Панель адміна
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
