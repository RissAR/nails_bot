import React, { useState, useEffect } from 'react';
import { X, Calendar, Clock, User, Phone, CheckCircle2, Sparkles, Loader2 } from 'lucide-react';
import { Master, Service } from '../types';

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  service: Service;
  master: Master;
  date: string;
  time: string;
  telegramUser?: {
    id?: number;
    first_name?: string;
    phone_number?: string;
  } | null;
  onSubmit: (data: { name: string; phone: string; notes?: string }) => Promise<void>;
  isSubmitting: boolean;
  bookingSuccess: boolean;
  onSuccessDone: () => void;
}

export const BookingModal: React.FC<BookingModalProps> = ({
  isOpen,
  onClose,
  service,
  master,
  date,
  time,
  telegramUser,
  onSubmit,
  isSubmitting,
  bookingSuccess,
  onSuccessDone,
}) => {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('+380');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (telegramUser?.first_name) {
      setName(telegramUser.first_name);
    }
    if (telegramUser?.phone_number) {
      setPhone(telegramUser.phone_number);
    }
  }, [telegramUser]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Будь ласка, вкажіть ваше ім'я");
      return;
    }

    if (!phone.trim() || phone.trim().length < 10) {
      setError('Вкажіть коректний контактний номер телефону');
      return;
    }

    try {
      await onSubmit({ name: name.trim(), phone: phone.trim(), notes: notes.trim() });
    } catch (err: any) {
      setError(err.message || 'Помилка при створенні бронювання');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/40 backdrop-blur-sm animate-fade-in">
      <div
        className="bg-nude-surface w-full max-w-md rounded-t-3xl sm:rounded-3xl border border-nude-border shadow-2xl overflow-hidden max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-5 py-4 border-b border-nude-border flex items-center justify-between bg-nude-bg/50">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-nude-primary" />
            <h3 className="font-bold text-nude-text text-base">
              {bookingSuccess ? 'Заявку прийнято!' : 'Підтвердження запису'}
            </h3>
          </div>
          <button
            type="button"
            onClick={bookingSuccess ? onSuccessDone : onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-nude-muted hover:text-nude-text hover:bg-nude-border/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-4">
          {bookingSuccess ? (
            <div className="py-6 text-center space-y-3">
              <div className="w-16 h-16 rounded-full bg-nude-greenLight text-nude-green flex items-center justify-center mx-auto shadow-inner animate-bounce-short">
                <CheckCircle2 className="w-10 h-10" />
              </div>

              <h4 className="text-lg font-bold text-nude-text">
                Чекаємо на вас у Sense Nail Studio!
              </h4>

              <p className="text-xs text-nude-muted leading-relaxed max-w-xs mx-auto">
                Ваша заявка успішно зареєстрована. Адміністратор зв'яжеться з вами у Telegram або за телефоном для остаточного підтвердження.
              </p>

              <div className="bg-nude-bg p-3.5 rounded-2xl border border-nude-border text-left text-xs space-y-1.5 mt-4">
                <div className="flex justify-between">
                  <span className="text-nude-muted">Послуга:</span>
                  <span className="font-bold text-nude-text">{service.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nude-muted">Майстер:</span>
                  <span className="font-semibold text-nude-text">{master.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nude-muted">Дата та час:</span>
                  <span className="font-semibold text-nude-text">{date} о {time}</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-nude-border/60">
                  <span className="text-nude-muted">Вартість:</span>
                  <span className="font-extrabold text-nude-primary text-sm">{service.price} грн</span>
                </div>
              </div>

              <button
                type="button"
                onClick={onSuccessDone}
                className="w-full mt-4 py-3 px-4 rounded-xl font-bold text-sm bg-nude-primary text-white hover:bg-nude-primaryHover transition-all shadow-sm"
              >
                Чудово, повернутися
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Summary pill */}
              <div className="bg-nude-bg p-3 rounded-2xl border border-nude-border text-xs space-y-1.5">
                <div className="font-bold text-nude-text text-sm mb-1">{service.name}</div>
                <div className="flex items-center gap-3 text-nude-muted">
                  <span className="flex items-center gap-1">
                    <User className="w-3.5 h-3.5 text-nude-primary" />
                    Майстер {master.name}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-nude-primary" />
                    {date}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-nude-primary" />
                    {time}
                  </span>
                </div>
              </div>

              {error && (
                <div className="p-2.5 rounded-xl bg-red-50 text-red-600 text-xs font-medium border border-red-200">
                  {error}
                </div>
              )}

              {/* Form fields */}
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-nude-text mb-1">
                    Ваше ім'я *
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-nude-muted absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      required
                      placeholder="Наприклад: Олена"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full pl-9 pr-3 py-2.5 bg-nude-bg rounded-xl border border-nude-border text-xs text-nude-text placeholder:text-nude-muted/60 focus:outline-none focus:border-nude-primary transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-nude-text mb-1">
                    Номер телефону *
                  </label>
                  <div className="relative">
                    <Phone className="w-4 h-4 text-nude-muted absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="tel"
                      required
                      placeholder="+380..."
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full pl-9 pr-3 py-2.5 bg-nude-bg rounded-xl border border-nude-border text-xs text-nude-text placeholder:text-nude-muted/60 focus:outline-none focus:border-nude-primary transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-nude-text mb-1">
                    Побажання чи коментар (необов'язково)
                  </label>
                  <textarea
                    rows={2}
                    placeholder="Наприклад: потрібне зняття старого покриття"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="w-full px-3 py-2 bg-nude-bg rounded-xl border border-nude-border text-xs text-nude-text placeholder:text-nude-muted/60 focus:outline-none focus:border-nude-primary transition-colors resize-none"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3 px-4 rounded-xl font-bold text-sm bg-nude-primary text-white hover:bg-nude-primaryHover disabled:opacity-60 transition-all flex items-center justify-center gap-2 shadow-sm"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Надсилання заявки...
                  </>
                ) : (
                  `Записатися (${service.price} грн)`
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
