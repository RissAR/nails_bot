export interface Service {
  id: number;
  category_id: number;
  category_name: string;
  name: string;
  description: string | null;
  duration_minutes: number;
  price: number;
  is_active: boolean;
  master_ids: number[];
}

export interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface Master {
  id: number;
  name: string;
  title: string;
  bio: string | null;
  is_active: boolean;
  service_ids: number[];
}

export interface BookingPayload {
  service_id: number;
  master_id: number;
  booking_date: string; // YYYY-MM-DD
  start_time: string;   // HH:MM
  client_name: string;
  client_phone: string;
  telegram_id?: number | null;
  notes?: string | null;
}

export interface BookingResult {
  id: number;
  status: string;
  booking_date: string;
  start_time: string;
  end_time: string;
  service_name: string;
  master_name: string;
  price: number;
}

export interface AdminBooking {
  id: number;
  client_name: string;
  client_phone: string | null;
  telegram_id: number | null;
  service_name: string;
  price: number;
  duration_minutes: number;
  master_name: string;
  booking_date: string;
  start_time: string;
  end_time: string;
  status: string;
  notes: string | null;
}

export interface AdminStats {
  pending_count: number;
  today_confirmed_count: number;
  total_revenue: number;
  total_clients: number;
}

export interface UserAuth {
  telegram_id: number | null;
  role: 'admin' | 'client';
  first_name: string | null;
  username: string | null;
  discount_percent?: number;
}
