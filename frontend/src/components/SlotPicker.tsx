import React, { useMemo } from 'react';
import { Calendar, Clock, Loader2 } from 'lucide-react';

interface SlotPickerProps {
  selectedDate: string;
  onSelectDate: (date: string) => void;
  slots: string[];
  isLoadingSlots: boolean;
  selectedSlot: string | null;
  onSelectSlot: (slot: string) => void;
  masterName?: string;
}

const UK_DAYS = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
const UK_MONTHS = [
  'січ', 'лют', 'бер', 'кві', 'тра', 'чер',
  'лип', 'сер', 'вер', 'жов', 'лис', 'гру'
];

export const SlotPicker: React.FC<SlotPickerProps> = ({
  selectedDate,
  onSelectDate,
  slots,
  isLoadingSlots,
  selectedSlot,
  onSelectSlot,
  masterName,
}) => {
  // Generate next 14 days
  const upcomingDays = useMemo(() => {
    const days = [];
    const today = new Date();

    for (let i = 0; i < 14; i++) {
      const d = new Date();
      d.setDate(today.getDate() + i);

      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      const dateStr = `${year}-${month}-${day}`;

      days.push({
        dateStr,
        dayOfWeek: UK_DAYS[d.getDay()],
        dayOfMonth: d.getDate(),
        monthName: UK_MONTHS[d.getMonth()],
        isToday: i === 0,
      });
    }
    return days;
  }, []);

  const triggerHaptic = () => {
    // @ts-ignore
    if (window.Telegram?.WebApp?.HapticFeedback) {
      // @ts-ignore
      window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-nude-text flex items-center gap-1.5">
          <span className="w-5 h-5 rounded-full bg-nude-primary text-white text-[11px] flex items-center justify-center font-bold">3</span>
          Оберіть дату та час
        </h2>
        {masterName && (
          <span className="text-xs text-nude-muted">
            Майстер: {masterName}
          </span>
        )}
      </div>

      {/* 14-day horizontal calendar */}
      <div className="flex gap-2 overflow-x-auto pb-1.5 pt-0.5 no-scrollbar -mx-1 px-1">
        {upcomingDays.map((item) => {
          const isSelected = selectedDate === item.dateStr;

          return (
            <button
              key={item.dateStr}
              type="button"
              onClick={() => {
                triggerHaptic();
                onSelectDate(item.dateStr);
              }}
              className={`flex flex-col items-center justify-center min-w-[54px] py-2 px-1 rounded-2xl border transition-all duration-200 shrink-0 ${
                isSelected
                  ? 'btn-caramel-3d text-white font-bold scale-[1.02] border-transparent'
                  : 'card-ceramic text-nude-text hover:border-nude-primary/40'
              }`}
            >
              <span className={`text-[10px] uppercase font-bold ${isSelected ? 'text-white/90' : 'text-nude-muted'}`}>
                {item.dayOfWeek}
              </span>
              <span className={`text-base font-extrabold my-0.5 ${isSelected ? 'text-white' : 'text-nude-text'}`}>
                {item.dayOfMonth}
              </span>
              <span className={`text-[10px] ${isSelected ? 'text-white/90' : 'text-nude-muted/80'}`}>
                {item.monthName}
              </span>
            </button>
          );
        })}
      </div>

      {/* Time slots */}
      <div className="card-ceramic rounded-2xl p-3.5 space-y-2.5">
        <div className="flex items-center justify-between text-xs text-nude-muted">
          <span className="flex items-center gap-1 font-medium">
            <Clock className="w-3.5 h-3.5 text-nude-primary" />
            Вільні віконця:
          </span>
          {isLoadingSlots && (
            <span className="flex items-center gap-1 text-nude-primary">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Оновлення...
            </span>
          )}
        </div>

        {isLoadingSlots ? (
          <div className="py-8 flex flex-col items-center justify-center text-nude-muted gap-2">
            <Loader2 className="w-6 h-6 animate-spin text-nude-primary" />
            <p className="text-xs">Шукаємо вільний час...</p>
          </div>
        ) : slots.length === 0 ? (
          <div className="py-6 text-center text-nude-muted bg-nude-bg/50 rounded-xl border border-dashed border-nude-border">
            <Calendar className="w-6 h-6 text-nude-muted/50 mx-auto mb-1.5" />
            <p className="text-xs font-medium">На цей день немає вільних слотів</p>
            <p className="text-[11px] text-nude-muted/80 mt-0.5">Оберіть іншу дату або іншого майстра</p>
          </div>
        ) : (
          <div className="grid grid-cols-4 sm:grid-cols-6 gap-2">
            {slots.map((slot) => {
              const isSelected = selectedSlot === slot;

              return (
                <button
                  key={slot}
                  type="button"
                  onClick={() => {
                    triggerHaptic();
                    onSelectSlot(slot);
                  }}
                  className={`py-2 px-1 rounded-xl text-xs font-bold transition-all duration-150 border text-center ${
                    isSelected
                      ? 'btn-caramel-3d text-white font-bold shadow-sm border-transparent scale-105'
                      : 'card-ceramic text-nude-text hover:border-nude-primary/50'
                  }`}
                >
                  {slot}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
