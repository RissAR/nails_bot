import React from 'react';
import { Check, Star, AlertCircle } from 'lucide-react';
import { Master, Service } from '../types';

interface MasterListProps {
  masters: Master[];
  selectedMaster: Master | null;
  onSelectMaster: (master: Master) => void;
  selectedService: Service | null;
}

export const MasterList: React.FC<MasterListProps> = ({
  masters,
  selectedMaster,
  onSelectMaster,
  selectedService,
}) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-nude-text flex items-center gap-1.5">
          <span className="w-5 h-5 rounded-full bg-nude-primary text-white text-[11px] flex items-center justify-center font-bold">2</span>
          Оберіть майстра
        </h2>
        {selectedService && (
          <span className="text-xs text-nude-muted">
            Для: {selectedService.name}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {masters.map((master) => {
          const isCompatible =
            !selectedService || master.service_ids.includes(selectedService.id);
          const isSelected = selectedMaster?.id === master.id;

          return (
            <div
              key={master.id}
              onClick={() => {
                if (isCompatible) {
                  onSelectMaster(master);
                }
              }}
              className={`p-3.5 rounded-2xl border transition-all duration-200 relative ${
                !isCompatible
                  ? 'opacity-50 bg-nude-bg border-nude-border/50 cursor-not-allowed'
                  : isSelected
                  ? 'bg-nude-accent/30 border-nude-primary shadow-sm cursor-pointer'
                  : 'bg-nude-surface border-nude-border/80 hover:border-nude-primary/40 cursor-pointer'
              }`}
            >
              <div className="flex items-start justify-between gap-2.5">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-nude-text">
                      {master.name}
                    </h3>
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-nude-primary bg-nude-accent/40 px-2 py-0.5 rounded-full">
                      <Star className="w-3 h-3 fill-nude-primary" />
                      {master.title}
                    </span>
                  </div>

                  {master.bio && (
                    <p className="text-xs text-nude-muted mt-1.5 leading-relaxed">
                      {master.bio}
                    </p>
                  )}

                  {!isCompatible && (
                    <div className="flex items-center gap-1 mt-2 text-[11px] font-medium text-amber-700 bg-amber-50 px-2 py-1 rounded-lg">
                      <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                      <span>Не виконує обрану послугу</span>
                    </div>
                  )}
                </div>

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
