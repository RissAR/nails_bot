import React, { useState } from 'react';
import {
  Bell,
  Calendar,
  Clock,
  DollarSign,
  Phone,
  RefreshCw,
  User,
  Users,
  CheckCircle,
  AlertCircle,
  Check,
  X,
  Loader2,
} from 'lucide-react';
import { api } from '../api/client';
import { AdminBooking, AdminStats, Master } from '../types';

interface AdminDashboardProps {
  bookings: AdminBooking[];
  stats: AdminStats | null;
  masters: Master[];
  onRefresh: () => void;
  isLoading: boolean;
  onStatusUpdate?: (id: number, newStatus: 'confirmed' | 'rejected') => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({
  bookings,
  stats,
  masters,
  onRefresh,
  isLoading,
  onStatusUpdate,
}) => {
  const [processingId, setProcessingId] = useState<number | null>(null);
  const pendingBookings = bookings.filter((b) => b.status === 'pending');
  const todayStr = new Date().toISOString().split('T')[0];

  const handleAction = async (id: number, action: 'confirm' | 'reject') => {
    setProcessingId(id);
    try {
      if (action === 'confirm') {
        await api.confirmBooking(id);
        onStatusUpdate?.(id, 'confirmed');
      } else {
        await api.rejectBooking(id);
        onStatusUpdate?.(id, 'rejected');
      }
    } catch (err: any) {
      alert(err.message || 'Помилка оновлення статусу заявки');
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Title & Refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-nude-text">
            Панель керування салоном
          </h2>
          <p className="text-xs text-nude-muted">
            Огляд активних заявок та метрик
          </p>
        </div>

        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading}
          className="p-2 rounded-xl bg-nude-surface border border-nude-border text-nude-muted hover:text-nude-primary transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="bg-nude-surface p-3 rounded-2xl border border-nude-border shadow-sm">
          <div className="flex items-center justify-between text-nude-muted">
            <span className="text-[11px] font-semibold">Нові заявки</span>
            <Bell className="w-3.5 h-3.5 text-amber-500" />
          </div>
          <p className="text-xl font-extrabold text-nude-text mt-1.5">
            {stats?.pending_count ?? 0}
          </p>
          <span className="text-[10px] text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded font-medium">
            Очікують
          </span>
        </div>

        <div className="bg-nude-surface p-3 rounded-2xl border border-nude-border shadow-sm">
          <div className="flex items-center justify-between text-nude-muted">
            <span className="text-[11px] font-semibold">Сьогодні</span>
            <Calendar className="w-3.5 h-3.5 text-nude-primary" />
          </div>
          <p className="text-xl font-extrabold text-nude-text mt-1.5">
            {stats?.today_confirmed_count ?? 0}
          </p>
          <span className="text-[10px] text-nude-primary bg-nude-accent/30 px-1.5 py-0.5 rounded font-medium">
            Підтверджено
          </span>
        </div>

        <div className="bg-nude-surface p-3 rounded-2xl border border-nude-border shadow-sm">
          <div className="flex items-center justify-between text-nude-muted">
            <span className="text-[11px] font-semibold">Оборот</span>
            <DollarSign className="w-3.5 h-3.5 text-nude-green" />
          </div>
          <p className="text-xl font-extrabold text-nude-text mt-1.5">
            {stats?.total_revenue?.toFixed(0) ?? 0} <span className="text-xs font-bold text-nude-muted">грн</span>
          </p>
          <span className="text-[10px] text-nude-green bg-nude-greenLight px-1.5 py-0.5 rounded font-medium">
            За всіма заявками
          </span>
        </div>

        <div className="bg-nude-surface p-3 rounded-2xl border border-nude-border shadow-sm">
          <div className="flex items-center justify-between text-nude-muted">
            <span className="text-[11px] font-semibold">Клієнти</span>
            <Users className="w-3.5 h-3.5 text-nude-muted" />
          </div>
          <p className="text-xl font-extrabold text-nude-text mt-1.5">
            {stats?.total_clients ?? 0}
          </p>
          <span className="text-[10px] text-nude-muted bg-nude-bg px-1.5 py-0.5 rounded font-medium">
            У базі даних
          </span>
        </div>
      </div>

      {/* Masters on shift preview */}
      <div className="bg-nude-surface p-3.5 rounded-2xl border border-nude-border shadow-sm space-y-2">
        <h3 className="text-xs font-bold text-nude-text flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-nude-primary" />
          Команда майстрів студії
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
          {masters.map((m) => (
            <div key={m.id} className="p-2.5 rounded-xl bg-nude-bg border border-nude-border/70 flex items-center justify-between">
              <div>
                <span className="font-bold text-nude-text">{m.name}</span>
                <span className="text-[11px] text-nude-muted block">{m.title}</span>
              </div>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-nude-green bg-nude-greenLight px-2 py-0.5 rounded-full">
                <CheckCircle className="w-3 h-3" />
                Активна
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Pending Bookings List */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-nude-text uppercase tracking-wider">
            Черга заявок на підтвердження ({pendingBookings.length})
          </h3>
        </div>

        {pendingBookings.length === 0 ? (
          <div className="p-8 text-center bg-nude-surface rounded-2xl border border-nude-border text-nude-muted">
            <AlertCircle className="w-8 h-8 mx-auto mb-2 text-nude-muted/50" />
            <p className="text-xs font-bold text-nude-text">Нових заявок немає</p>
            <p className="text-[11px] text-nude-muted mt-0.5">Всі записи оброблено або очікується нове бронювання від клієнтів</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {pendingBookings.map((b) => (
              <div
                key={b.id}
                className="bg-nude-surface p-3.5 rounded-2xl border border-amber-200/80 shadow-sm relative space-y-2"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
                        #{b.id} Очікує
                      </span>
                      <span className="text-xs text-nude-muted font-medium">
                        {b.booking_date}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-nude-text mt-1">
                      {b.service_name}
                    </h4>
                  </div>
                  <span className="text-sm font-extrabold text-nude-primary">
                    {b.price} грн
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-nude-border/60">
                  <div className="flex items-center gap-1.5 text-nude-text">
                    <User className="w-3.5 h-3.5 text-nude-muted shrink-0" />
                    <span className="font-semibold truncate">{b.client_name}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-nude-text">
                    <Phone className="w-3.5 h-3.5 text-nude-muted shrink-0" />
                    <span className="truncate">{b.client_phone || 'Не вказано'}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-nude-muted">
                    <Clock className="w-3.5 h-3.5 text-nude-primary shrink-0" />
                    <span>Час: {b.start_time} - {b.end_time}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-nude-muted">
                    <span>Майстер: <b>{b.master_name}</b></span>
                  </div>
                </div>

                {b.notes && (
                  <p className="text-[11px] text-nude-muted bg-nude-bg p-2 rounded-lg italic">
                    Коментар: "{b.notes}"
                  </p>
                )}

                {/* Interactive Action Buttons */}
                <div className="flex items-center gap-2 pt-2 border-t border-nude-border/60">
                  <button
                    type="button"
                    disabled={processingId === b.id}
                    onClick={() => handleAction(b.id, 'confirm')}
                    className="flex-1 py-2 px-3 rounded-xl bg-nude-greenLight text-nude-green font-bold text-xs hover:bg-nude-greenLight/80 active:scale-95 transition-all flex items-center justify-center gap-1.5 shadow-sm disabled:opacity-50"
                  >
                    {processingId === b.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Check className="w-3.5 h-3.5" />
                    )}
                    <span>Підтвердити</span>
                  </button>
                  <button
                    type="button"
                    disabled={processingId === b.id}
                    onClick={() => handleAction(b.id, 'reject')}
                    className="flex-1 py-2 px-3 rounded-xl bg-red-50 text-red-600 font-bold text-xs hover:bg-red-100 active:scale-95 transition-all flex items-center justify-center gap-1.5 shadow-sm disabled:opacity-50"
                  >
                    {processingId === b.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <X className="w-3.5 h-3.5" />
                    )}
                    <span>Відхилити</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
