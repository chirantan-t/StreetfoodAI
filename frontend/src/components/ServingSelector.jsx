import React from 'react';
import { Scale } from 'lucide-react';

export default function ServingSelector({ currentServing, onServingChange, servingWeightG }) {
  const options = [
    { id: 'Small', label: 'Small Portion', desc: 'Single piece / half plate' },
    { id: 'Regular', label: 'Regular Portion', desc: 'Standard street serving' },
    { id: 'Large', label: 'Large Portion', desc: 'Double piece / full plate' },
  ];

  return (
    <div className="bg-white rounded-2xl border border-stone-200/80 shadow-xs p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Scale className="w-4 h-4 text-saffron-600" />
          <h3 className="text-sm font-bold text-charcoal-900">Serving Size & Portion Adjustment</h3>
        </div>
        {servingWeightG && (
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
            Est. Weight: ~{servingWeightG}g
          </span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2.5">
        {options.map((opt) => {
          const isSelected = currentServing === opt.id;
          return (
            <button
              key={opt.id}
              type="button"
              onClick={() => onServingChange(opt.id)}
              className={`p-3 rounded-xl text-left border transition-all ${
                isSelected
                  ? 'border-saffron-500 bg-saffron-50/60 ring-2 ring-saffron-400/20'
                  : 'border-stone-200 hover:border-stone-300 bg-stone-50/50 hover:bg-stone-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <span
                  className={`text-xs font-bold ${isSelected ? 'text-saffron-900' : 'text-charcoal-900'}`}
                >
                  {opt.id}
                </span>
                <span
                  className={`w-2 h-2 rounded-full ${isSelected ? 'bg-saffron-500' : 'bg-transparent'}`}
                />
              </div>
              <p className="text-[11px] text-stone-500 mt-1 line-clamp-1">{opt.desc}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
