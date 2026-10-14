import React, { useState, useEffect } from 'react';
import { Service } from '../types';

interface ServiceListProps {
  services: Service[];
  selectedService: Service | null;
  onSelectService: (service: Service) => void;
}

export const ServiceList: React.FC<ServiceListProps> = ({
  services,
  selectedService,
  onSelectService,
}) => {
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<string>(() => {
    if (selectedService) {
      const cat = selectedService.category_name.toLowerCase();
      if (cat.includes('моделювання') || cat.includes('нарощування')) return 'extensions';
      if (cat.includes('догляд') || cat.includes('add-on')) return 'care';
      return 'complexes';
    }
    return 'complexes';
  });

  const filterTabs = [
    { id: 'complexes', label: 'Комплекси' },
    { id: 'extensions', label: 'Нарощування' },
    { id: 'care', label: 'Догляд' },
    { id: 'all', label: 'Всі' },
  ];

  useEffect(() => {
    if (selectedService && activeCategoryFilter !== 'all') {
      const cat = selectedService.category_name.toLowerCase();
      if (cat.includes('моделювання') || cat.includes('нарощування')) {
        if (activeCategoryFilter !== 'extensions') setActiveCategoryFilter('extensions');
      } else if (cat.includes('догляд') || cat.includes('add-on')) {
        if (activeCategoryFilter !== 'care') setActiveCategoryFilter('care');
      } else if (cat.includes('комплекс')) {
        if (activeCategoryFilter !== 'complexes') setActiveCategoryFilter('complexes');
      }
    }
  }, [selectedService]);

  const filteredServices = services.filter((s) => {
    if (activeCategoryFilter === 'all') return true;
    if (activeCategoryFilter === 'complexes') return s.category_name.toLowerCase().includes('комплекс');
    if (activeCategoryFilter === 'extensions') return s.category_name.toLowerCase().includes('моделювання') || s.category_name.toLowerCase().includes('нарощування');
    if (activeCategoryFilter === 'care') return s.category_name.toLowerCase().includes('догляд') || s.category_name.toLowerCase().includes('add-on');
    return true;
  });

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-nude-text flex items-center gap-1.5">
          <span className="w-5 h-5 rounded-full bg-nude-primary text-white text-[11px] flex items-center justify-center font-bold">1</span>
          Оберіть послугу
        </h2>
        <span className="text-xs text-nude-muted">
          {filteredServices.length} доступно
        </span>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-1.5 overflow-x-auto pb-0.5 no-scrollbar">
        {filterTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveCategoryFilter(tab.id)}
            className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
              activeCategoryFilter === tab.id
                ? 'chip-active-3d text-white shadow-xs'
                : 'card-ceramic text-nude-muted hover:text-nude-text'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Services List Tiles */}
      <div className="space-y-1.5">
        {filteredServices.map((service) => {
          const isSelected = selectedService?.id === service.id;

          return (
            <div
              key={service.id}
              onClick={() => onSelectService(service)}
              className={`py-2.5 px-3 rounded-xl border transition-all duration-150 cursor-pointer ${
                isSelected
                  ? 'card-ceramic-active'
                  : 'card-ceramic hover:border-nude-primary/50'
              }`}
            >
              {/* Upper row: Radio + Name on left, duration + price on right */}
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className={`w-4 h-4 rounded-full border flex items-center justify-center shrink-0 transition-all ${
                      isSelected
                        ? 'border-[#C28751] bg-gradient-to-br from-[#D49660] to-[#B7763B] shadow-xs'
                        : 'border-nude-border bg-nude-bg'
                    }`}
                  >
                    {isSelected && (
                      <div className="w-1.5 h-1.5 rounded-full bg-white" />
                    )}
                  </div>
                  <span className="text-xs font-bold text-nude-text truncate">
                    {service.name}
                  </span>
                </div>

                <div className="text-xs font-bold text-nude-text whitespace-nowrap shrink-0">
                  {service.duration_minutes} хв • {Math.round(service.price)} ₴
                </div>
              </div>

              {/* Lower row: Short description */}
              {service.description && (
                <div className="text-[10px] text-nude-muted truncate max-w-[240px] pl-6 mt-0.5">
                  {service.description}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
