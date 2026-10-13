import React, { useState, useEffect, useCallback } from 'react';
import { Sparkles, Calendar, Clock, ChevronRight, AlertTriangle } from 'lucide-react';
import { Header } from './components/Header';
import { ServiceList } from './components/ServiceList';
import { MasterList } from './components/MasterList';
import { SlotPicker } from './components/SlotPicker';
import { BookingModal } from './components/BookingModal';
import { AdminDashboard } from './components/AdminDashboard';
import { api } from './api/client';
import {
  AdminBooking,
  AdminStats,
  BookingPayload,
  Master,
  Service,
  UserAuth,
} from './types';

export const App: React.FC = () => {
  // 1. Hooks - State declarations at the very top (Rules of Hooks)
  const [activeTab, setActiveTab] = useState<'client' | 'admin'>('client');
  const [auth, setAuth] = useState<UserAuth | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [masters, setMasters] = useState<Master[]>([]);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedMaster, setSelectedMaster] = useState<Master | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    const today = new Date();
    const y = today.getFullYear();
    const m = String(today.getMonth() + 1).padStart(2, '0');
    const d = String(today.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  });
  const [slots, setSlots] = useState<string[]>([]);
  const [isLoadingSlots, setIsLoadingSlots] = useState<boolean>(false);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);

  // Modal & Booking state
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [bookingSuccess, setBookingSuccess] = useState<boolean>(false);

  // Admin state
  const [adminBookings, setAdminBookings] = useState<AdminBooking[]>([]);
  const [adminStats, setAdminStats] = useState<AdminStats | null>(null);
  const [isLoadingAdmin, setIsLoadingAdmin] = useState<boolean>(false);

  // Global loading & error
  const [isLoadingInitial, setIsLoadingInitial] = useState<boolean>(true);
  const [globalError, setGlobalError] = useState<string | null>(null);

  // 2. Telegram WebApp initialization
  useEffect(() => {
    // @ts-ignore
    const tg = window.Telegram?.WebApp;
    if (tg) {
      try {
        tg.ready();
        tg.expand();
      } catch (e) {
        console.error('Error initializing Telegram WebApp', e);
      }
    }
  }, []);

  // 3. Load initial catalog & auth
  useEffect(() => {
    const initApp = async () => {
      try {
        setIsInitialLoad(true);
        // @ts-ignore
        const initData = window.Telegram?.WebApp?.initData || '';
        // @ts-ignore
        const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
        const tgId = tgUser?.id;

        const [authData, servicesData, mastersData] = await Promise.all([
          api.getAuthMe(initData, tgId),
          api.getServices(),
          api.getMasters(),
        ]);

        setAuth(authData);
        setServices(servicesData);
        setMasters(mastersData);

        // Check deep-link params (?role=admin, ?service_id=X)
        const urlParams = new URLSearchParams(window.location.search);
        const reqRole = urlParams.get('role');
        const reqServiceId = urlParams.get('service_id');

        if (reqRole === 'admin' && authData.role === 'admin') {
          setActiveTab('admin');
        }

        // Pre-select requested or first service and compatible master
        if (servicesData.length > 0) {
          const targetSvc = reqServiceId
            ? servicesData.find((s) => s.id === Number(reqServiceId)) || servicesData[0]
            : servicesData[0];
          setSelectedService(targetSvc);
          const compatible = mastersData.find((m) =>
            m.service_ids.includes(targetSvc.id)
          );
          if (compatible) {
            setSelectedMaster(compatible);
          }
        }
      } catch (err: any) {
        setGlobalError(err.message || 'Не вдалося завантажити дані студії');
      } finally {
        setIsLoadingInitial(false);
      }
    };

    initApp();
  }, []);

  // Helper setter for initial load
  const setIsInitialLoad = (val: boolean) => setIsLoadingInitial(val);

  // 4. Load slots when master, service, or date changes
  useEffect(() => {
    if (!selectedMaster || !selectedService || !selectedDate) {
      setSlots([]);
      return;
    }

    let isMounted = true;
    const fetchSlots = async () => {
      setIsLoadingSlots(true);
      try {
        const availableSlots = await api.getSlots(
          selectedMaster.id,
          selectedDate,
          selectedService.id
        );
        if (isMounted) {
          setSlots(availableSlots);
          // Auto-select first slot or reset if current slot is no longer available
          setSelectedSlot((prev) => (prev && availableSlots.includes(prev) ? prev : null));
        }
      } catch (err) {
        if (isMounted) setSlots([]);
      } finally {
        if (isMounted) setIsLoadingSlots(false);
      }
    };

    fetchSlots();
    return () => {
      isMounted = false;
    };
  }, [selectedMaster, selectedService, selectedDate]);

  // 5. Load admin data when switching to admin tab
  const loadAdminData = useCallback(async () => {
    if (auth?.role !== 'admin') return;
    setIsLoadingAdmin(true);
    try {
      const [bookingsData, statsData] = await Promise.all([
        api.getAdminBookings(),
        api.getAdminStats(),
      ]);
      setAdminBookings(bookingsData);
      setAdminStats(statsData);
    } catch (e) {
      console.error('Error fetching admin data', e);
    } finally {
      setIsLoadingAdmin(false);
    }
  }, [auth]);

  useEffect(() => {
    if (activeTab === 'admin') {
      loadAdminData();
    }
  }, [activeTab, loadAdminData]);

  // Handle service selection and compatibility
  const handleSelectService = (service: Service) => {
    setSelectedService(service);
    // If current master doesn't perform this service, pick first compatible master
    if (selectedMaster && !selectedMaster.service_ids.includes(service.id)) {
      const compatible = masters.find((m) => m.service_ids.includes(service.id));
      if (compatible) setSelectedMaster(compatible);
    }
    setSelectedSlot(null);
  };

  // Handle booking submission
  const handleBookingSubmit = async (formData: {
    name: string;
    phone: string;
    notes?: string;
  }) => {
    if (!selectedService || !selectedMaster || !selectedSlot) return;

    setIsSubmitting(true);
    try {
      // @ts-ignore
      const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;

      const payload: BookingPayload = {
        service_id: selectedService.id,
        master_id: selectedMaster.id,
        booking_date: selectedDate,
        start_time: selectedSlot,
        client_name: formData.name,
        client_phone: formData.phone,
        telegram_id: tgUser?.id || auth?.telegram_id || null,
        notes: formData.notes || null,
      };

      await api.createBooking(payload);
      setBookingSuccess(true);

      // Refresh slots
      const updatedSlots = await api.getSlots(
        selectedMaster.id,
        selectedDate,
        selectedService.id
      );
      setSlots(updatedSlots);
      setSelectedSlot(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBookingDone = () => {
    setIsModalOpen(false);
    setBookingSuccess(false);
  };

  // 6. Render
  if (isLoadingInitial) {
    return (
      <div className="min-h-screen bg-nude-bg flex flex-col items-center justify-center p-6 text-center">
        <div className="w-12 h-12 rounded-full bg-nude-accent flex items-center justify-center text-nude-primary shadow-inner mb-4 animate-pulse">
          <Sparkles className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-nude-text">Sense Nail Studio</h2>
        <p className="text-xs text-nude-muted mt-1">Завантажуємо каталог та розклад...</p>
      </div>
    );
  }

  if (globalError) {
    return (
      <div className="min-h-screen bg-nude-bg flex flex-col items-center justify-center p-6 text-center">
        <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center mb-4">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-nude-text">Помилка завантаження</h2>
        <p className="text-xs text-nude-muted mt-1 max-w-xs">{globalError}</p>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-nude-primary text-white rounded-xl text-xs font-bold"
        >
          Спробувати знову
        </button>
      </div>
    );
  }

  // @ts-ignore
  const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;

  return (
    <div className="min-h-screen bg-nude-bg flex flex-col max-w-lg mx-auto shadow-2xl relative pb-28">
      {/* Header */}
      <Header
        isAdmin={auth?.role === 'admin'}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        userName={auth?.first_name || tgUser?.first_name}
      />

      {/* Main Container */}
      <main className="p-4 space-y-6">
        {activeTab === 'admin' ? (
          <AdminDashboard
            bookings={adminBookings}
            stats={adminStats}
            masters={masters}
            onRefresh={loadAdminData}
            isLoading={isLoadingAdmin}
          />
        ) : (
          <>
            {/* Step 1: Services */}
            <ServiceList
              services={services}
              selectedService={selectedService}
              onSelectService={handleSelectService}
            />

            {/* Step 2: Masters */}
            <MasterList
              masters={masters}
              selectedMaster={selectedMaster}
              onSelectMaster={setSelectedMaster}
              selectedService={selectedService}
            />

            {/* Step 3: Slots */}
            {selectedMaster && selectedService && (
              <SlotPicker
                selectedDate={selectedDate}
                onSelectDate={setSelectedDate}
                slots={slots}
                isLoadingSlots={isLoadingSlots}
                selectedSlot={selectedSlot}
                onSelectSlot={setSelectedSlot}
                masterName={selectedMaster.name}
              />
            )}
          </>
        )}
      </main>

      {/* Sticky Bottom Bar for Clients */}
      {activeTab === 'client' && selectedService && (
        <div className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto p-3.5 bg-nude-surface/95 backdrop-blur-md border-t border-nude-border z-40 shadow-lg">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="text-[11px] text-nude-muted font-medium flex items-center gap-1.5">
                <span>{selectedService.name}</span>
                <span>•</span>
                <span>{selectedService.duration_minutes} хв</span>
              </div>
              <div className="flex items-baseline gap-1 mt-0.5">
                <span className="text-lg font-black text-nude-text">
                  {selectedService.price} грн
                </span>
                {selectedSlot && (
                  <span className="text-xs text-nude-primary font-bold ml-1">
                    на {selectedSlot}
                  </span>
                )}
              </div>
            </div>

            <button
              type="button"
              disabled={!selectedSlot}
              onClick={() => setIsModalOpen(true)}
              className={`px-5 py-3 rounded-2xl font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm ${
                selectedSlot
                  ? 'bg-nude-primary text-white hover:bg-nude-primaryHover active:scale-95'
                  : 'bg-nude-border/70 text-nude-muted/80 cursor-not-allowed'
              }`}
            >
              <span>{selectedSlot ? 'Записатися' : 'Оберіть час'}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Booking Confirmation Modal */}
      {selectedService && selectedMaster && selectedSlot && (
        <BookingModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          service={selectedService}
          master={selectedMaster}
          date={selectedDate}
          time={selectedSlot}
          telegramUser={tgUser}
          onSubmit={handleBookingSubmit}
          isSubmitting={isSubmitting}
          bookingSuccess={bookingSuccess}
          onSuccessDone={handleBookingDone}
        />
      )}
    </div>
  );
};
