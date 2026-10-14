import React from 'react';
import { Check } from 'lucide-react';
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
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-nude-text flex items-center gap-1.5">
          <span className="w-5 h-5 rounded-full bg-nude-primary text-white text-[11px] flex items-center justify-center font-bold">2</span>
          Оберіть майстра
        </h2>
        {selectedService && (
          <span className="text-xs text-nude-muted truncate max-w-[180px]">
            Для: {selectedService.name}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2">
        {masters.map((master) => {
          const isCompatible =
            !selectedService || master.service_ids.includes(selectedService.id);
          const isSelected = selectedMaster?.id === master.id;

          const expText = master.title.toLowerCase().includes('top')
            ? '4 роки досвіду'
            : '2 роки досвіду';

          return (
            <div
              key={master.id}
              onClick={() => {
                if (isCompatible) {
                  onSelectMaster(master);
                }
              }}
              className={`p-2.5 rounded-xl border transition-all duration-150 relative min-h-[65px] flex items-center gap-2.5 ${
                !isCompatible
                  ? 'opacity-40 bg-nude-bg border-nude-border/50 cursor-not-allowed'
                  : isSelected
                  ? 'card-ceramic-active cursor-pointer'
                  : 'card-ceramic hover:border-nude-primary/50 cursor-pointer'
              }`}
            >
              {/* Round Avatar with initial */}
              <div
                className={`w-9 h-9 rounded-full shrink-0 flex items-center justify-center font-bold text-xs shadow-inner ${
                  isSelected
                    ? 'bg-gradient-to-br from-[#D49660] to-[#B7763B] text-white shadow-sm'
                    : 'bg-gradient-to-br from-[#FAF5EE] to-[#EBD9C8] text-nude-primary border border-nude-border/60'
                }`}
              >
                {master.name.charAt(0)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1">
                  <span className="text-xs font-bold text-nude-text truncate">
                    {master.name}
                  </span>
                  {isSelected && (
                    <span className="w-3.5 h-3.5 rounded-full bg-gradient-to-br from-[#D49660] to-[#B7763B] flex items-center justify-center text-white shrink-0 shadow-xs">
                      <Check className="w-2.5 h-2.5 stroke-[3]" />
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="text-[10px] font-semibold text-nude-primary bg-nude-accent/50 px-1.5 py-0.5 rounded leading-none">
                    {master.title}
                  </span>
                </div>

                <div className="text-[10px] text-nude-muted mt-0.5">
                  {expText}
                </div>

                {!isCompatible && (
                  <div className="text-[9px] text-amber-700 font-medium truncate mt-0.5">
                    Не виконує
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
