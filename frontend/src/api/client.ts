import {
  AdminBooking,
  AdminStats,
  BookingPayload,
  BookingResult,
  Category,
  Master,
  Service,
  UserAuth,
} from '../types';

const API_BASE = '/api';

function getHeaders(contentType: boolean = false): Record<string, string> {
  const headers: Record<string, string> = {};
  if (contentType) headers['Content-Type'] = 'application/json';
  const initData = (window as any).Telegram?.WebApp?.initData;
  if (initData) {
    headers['X-Telegram-Init-Data'] = initData;
  }
  return headers;
}

export const api = {
  async getServices(): Promise<Service[]> {
    const res = await fetch(`${API_BASE}/services`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Помилка завантаження послуг');
    return res.json();
  },

  async getCategories(): Promise<Category[]> {
    const res = await fetch(`${API_BASE}/services/categories`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Помилка завантаження категорій');
    return res.json();
  },

  async getMasters(): Promise<Master[]> {
    const res = await fetch(`${API_BASE}/masters`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Помилка завантаження майстрів');
    return res.json();
  },

  async getSlots(masterId: number, date: string, serviceId: number): Promise<string[]> {
    const params = new URLSearchParams({
      master_id: masterId.toString(),
      date,
      service_id: serviceId.toString(),
    });
    const res = await fetch(`${API_BASE}/slots?${params.toString()}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Помилка завантаження вільних слотів');
    return res.json();
  },

  async createBooking(payload: BookingPayload): Promise<BookingResult> {
    const res = await fetch(`${API_BASE}/bookings`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const error: any = new Error(err.detail || 'Помилка створення бронювання');
      error.status = res.status;
      throw error;
    }
    return res.json();
  },

  async getAdminBookings(): Promise<AdminBooking[]> {
    const res = await fetch(`${API_BASE}/admin/bookings`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Помилка завантаження заявок');
    return res.json();
  },

  async confirmBooking(id: number): Promise<AdminBooking> {
    const res = await fetch(`${API_BASE}/admin/bookings/${id}/confirm`, {
      method: 'PATCH',
      headers: getHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Помилка підтвердження запису');
    }
    return res.json();
  },

  async rejectBooking(id: number): Promise<AdminBooking> {
    const res = await fetch(`${API_BASE}/admin/bookings/${id}/reject`, {
      method: 'PATCH',
      headers: getHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Помилка відхилення запису');
    }
    return res.json();
  },

  async getAdminStats(): Promise<AdminStats> {
    const res = await fetch(`${API_BASE}/admin/stats`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Помилка завантаження статистики');
    return res.json();
  },

  async getAuthMe(initData?: string, tgId?: number): Promise<UserAuth> {
    const params = new URLSearchParams();
    if (initData) params.append('init_data', initData);
    if (tgId) params.append('tg_id', tgId.toString());

    const res = await fetch(`${API_BASE}/auth/me?${params.toString()}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Помилка авторизації');
    return res.json();
  },
};
