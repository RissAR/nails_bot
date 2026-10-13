import React, { useState } from 'react';
import { Check, Clock, Sparkles } from 'lucide-react';
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
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<string>('all');

  const filterTabs = [
    { id: 'all', label: 'Всі' },
    { id: 'complexes', label: 'Комплекси' },
    { id: 'extensions', label: 'Нарощування' },
    { id: 'care', label: 'Догляд' },
  ];

  const filteredServices = services.filter((s) => {
    if (activeCategoryFilter === 'all') return true;
    if (activeCategoryFilter === 'complexes') return s.category_name.toLowerCase().includes('комплекс');
    if (activeCategoryFilter === 'extensions') return s.category_name.toLowerCase().includes('моделювання') || s.category_name.toLowerCase().includes('нарощування');
    if (activeCategoryFilter === 'care') return s.category_name.toLowerCase().includes('догляд') || s.category_name.toLowerCase().includes('add-on');
    return true;
  });

  return (
    <div className="space-y-3">
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
      <div className="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar">
        {filterTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveCategoryFilter(tab.id)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
              activeCategoryFilter === tab.id
                ? 'bg-nude-primary text-white shadow-sm'
                : 'bg-nude-surface text-nude-muted border border-nude-border hover:text-nude-text'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Services Cards */}
      <div className="grid gap-2.5">
        {filteredServices.map((service) => {
          const isSelected = selectedService?.id === service.id;

          return (
            <div
              key={service.id}
              onClick={() => onSelectService(service)}
              className={`p-3.5 rounded-2xl border transition-all duration-200 cursor-pointer relative ${
                isSelected
                  ? 'bg-nude-accent/30 border-nude-primary shadow-sm'
                  : 'bg-nude-surface border-nude-border/80 hover:border-nude-primary/40'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-nude-primary bg-nude-accent/50 px-2 py-0.5 rounded-full">
                      {service.category_name}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-nude-text mt-1.5 leading-snug">
                    {service.name}
                  </h3>

                  {service.description && (
                    <p className="text-xs text-nude-muted mt-1 line-clamp-2 leading-relaxed">
                      {service.description}
                    </p>
                  )}

                  <div className="flex items-center gap-3 mt-2.5 text-xs text-nude-muted">
                    <span className="flex items-center gap-1 font-medium">
                      <Clock className="w-3.5 h-3.5 text-nude-primary" />
                      {service.duration_minutes} хв
                    </span>
                    <span className="font-bold text-nude-text text-sm">
                      {service.price} грн
                    </span>
                  </div>
                </div>

                {/* Selection Indicator */}
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 border transition-all ${
                    isSelected
                      ? 'bg-nude-primary border-nude-primary text-white shadow-sm'
                      : 'border-nude-border bg-nude-bg text-transparent'
                  }`}
                >
                  <Check className="w-3.5 h-3.5 stroke-[3]" />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
