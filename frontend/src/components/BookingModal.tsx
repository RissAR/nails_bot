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
  discountPercent?: number;
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
  discountPercent = 0,
  onSubmit,
  isSubmitting,
  bookingSuccess,
  onSuccessDone,
}) => {
  const [name, setName] = useState('');
  const [phoneSuffix, setPhoneSuffix] = useState('');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);

  const finalPrice =
    discountPercent > 0
      ? Math.round(service.price * (1 - discountPercent / 100))
      : service.price;

  useEffect(() => {
    if (telegramUser?.first_name) {
      const cleanName = telegramUser.first_name
        .replace(/[^А-Яа-яІіЇїЄєҐґ'\s\-]/g, '')
        .slice(0, 40);
      if (cleanName) setName(cleanName);
    }
    if (telegramUser?.phone_number) {
      const rawDigits = telegramUser.phone_number.replace(/\D/g, '');
      let suffix = rawDigits;
      if (suffix.startsWith('380')) {
        suffix = suffix.slice(3);
      }
      setPhoneSuffix(suffix.slice(0, 9));
    }
  }, [telegramUser]);

  const formatPhoneDigits = (raw: string) => {
    const d = raw.slice(0, 9);
    if (d.length <= 2) return d;
    if (d.length <= 5) return `${d.slice(0, 2)} ${d.slice(2)}`;
    if (d.length <= 7) return `${d.slice(0, 2)} ${d.slice(2, 5)} ${d.slice(5)}`;
    return `${d.slice(0, 2)} ${d.slice(2, 5)} ${d.slice(5, 7)} ${d.slice(7, 9)}`;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const digitsOnly = e.target.value.replace(/\D/g, '');
    let suffix = digitsOnly;
    if (suffix.startsWith('380')) {
      suffix = suffix.slice(3);
    }
    setPhoneSuffix(suffix.slice(0, 9));
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    const filtered = val.replace(/[^А-Яа-яІіЇїЄєҐґ'\s\-]/g, '');
    if (filtered.length <= 40) {
      setName(filtered);
    }
  };

  const isFormValid = name.trim().length >= 2 && name.trim().length <= 40 && phoneSuffix.length === 9;

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (name.trim().length < 2 || name.trim().length > 40) {
      setError("Ім'я має містити виключно українські літери (від 2 до 40 символів)");
      return;
    }

    if (phoneSuffix.length !== 9) {
      setError("Номер телефону має бути у форматі +380XXXXXXXXX (9 цифр після коду країни)");
      return;
    }

    const fullPhone = `+380${phoneSuffix}`;

    try {
      await onSubmit({ name: name.trim(), phone: fullPhone, notes: notes.trim() });
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
                  <div className="flex items-center gap-1.5">
                    {discountPercent > 0 && (
                      <span className="text-xs text-nude-muted line-through">{service.price} грн</span>
                    )}
                    <span className="font-extrabold text-nude-primary text-sm">{finalPrice} грн</span>
                  </div>
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
                <div className="flex items-center justify-between">
                  <div className="font-bold text-nude-text text-sm">{service.name}</div>
                  <div className="flex items-center gap-1.5">
                    {discountPercent > 0 ? (
                      <>
                        <span className="text-[11px] text-nude-muted line-through">{service.price} грн</span>
                        <span className="font-extrabold text-nude-primary text-xs">{finalPrice} грн</span>
                      </>
                    ) : (
                      <span className="font-extrabold text-nude-primary text-xs">{service.price} грн</span>
                    )}
                  </div>
                </div>
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

              {discountPercent > 0 && (
                <div className="p-2.5 rounded-xl bg-nude-greenLight text-nude-green text-xs font-bold flex items-center justify-between border border-nude-green/20">
                  <span>🏷 Ваша персональна знижка:</span>
                  <span className="bg-nude-surface px-2 py-0.5 rounded-lg shadow-xs">-{discountPercent}%</span>
                </div>
              )}

              {error && (
                <div className="p-2.5 rounded-xl bg-red-50 text-red-600 text-xs font-medium border border-red-200">
                  {error}
                </div>
              )}

              {/* Form fields */}
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="block text-xs font-semibold text-nude-text">
                      Ваше ім'я *
                    </label>
                    <span className="text-[10px] text-nude-muted">
                      {name.length}/40
                    </span>
                  </div>
                  <div className="relative">
                    <User className="w-4 h-4 text-nude-muted absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="text"
                      required
                      placeholder="Наприклад: Олена"
                      value={name}
                      onChange={handleNameChange}
                      maxLength={40}
                      className="w-full pl-9 pr-3 py-2.5 bg-nude-bg rounded-xl border border-nude-border text-xs text-nude-text placeholder:text-nude-muted/60 focus:outline-none focus:border-nude-primary transition-colors"
                    />
                  </div>
                  <p className="text-[10px] text-nude-muted mt-1 px-0.5">
                    Лише українські літери (від 2 до 40 символів)
                  </p>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="block text-xs font-semibold text-nude-text">
                      Номер телефону *
                    </label>
                    <span className={`text-[10px] ${phoneSuffix.length === 9 ? 'text-nude-green font-semibold' : 'text-nude-muted'}`}>
                      {phoneSuffix.length}/9 цифр
                    </span>
                  </div>
                  <div className="relative flex items-center">
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5 pointer-events-none select-none">
                      <Phone className="w-4 h-4 text-nude-muted" />
                      <span className="text-xs font-bold text-nude-text border-r border-nude-border pr-1.5">+380</span>
                    </div>
                    <input
                      type="tel"
                      inputMode="numeric"
                      required
                      placeholder="97 123 45 67"
                      value={formatPhoneDigits(phoneSuffix)}
                      onChange={handlePhoneChange}
                      maxLength={12}
                      className="w-full pl-20 pr-3 py-2.5 bg-nude-bg rounded-xl border border-nude-border text-xs text-nude-text font-medium placeholder:text-nude-muted/60 focus:outline-none focus:border-nude-primary transition-colors"
                    />
                  </div>
                  <p className="text-[10px] text-nude-muted mt-1 px-0.5">
                    Формат: +380XXXXXXXXX (9 цифр після +380)
                  </p>
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
                disabled={isSubmitting || !isFormValid}
                className="w-full py-3 px-4 rounded-xl font-bold text-sm bg-nude-primary text-white hover:bg-nude-primaryHover disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-sm"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Надсилання заявки...
                  </>
                ) : (
                  `Записатися (${finalPrice} грн)`
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
