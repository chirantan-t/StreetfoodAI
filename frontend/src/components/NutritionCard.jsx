import React from 'react';
import { Flame, Beef, Wheat, Droplets, Info, BookOpen, AlertTriangle } from 'lucide-react';

export default function NutritionCard({ nutrition, servingSize }) {
  if (!nutrition || !nutrition.is_available) {
    return (
      <div className="bg-white rounded-2xl border border-stone-200/80 shadow-xs p-6">
        <div className="flex items-center space-x-2 text-stone-500 mb-2">
          <Info className="w-5 h-5 text-amber-500" />
          <h3 className="text-base font-bold text-charcoal-900">Nutritional Estimation Withheld</h3>
        </div>
        <p className="text-xs text-stone-600 leading-relaxed">
          {nutrition?.notes_uncertainty ||
            'Nutritional values are withheld for uncertain or unclassified food items to prevent incorrect dietary tracking.'}
        </p>
      </div>
    );
  }

  const {
    food_name,
    calories,
    protein,
    carbohydrates,
    fat,
    fiber,
    serving_weight_g,
    serving_description,
    data_source,
    source_reference,
    notes_uncertainty,
    disclaimer,
  } = nutrition;

  // Compute macro proportions for visual bar
  const totalMacros = (protein || 0) + (carbohydrates || 0) + (fat || 0);
  const pPct = totalMacros > 0 ? Math.round(((protein || 0) / totalMacros) * 100) : 0;
  const cPct = totalMacros > 0 ? Math.round(((carbohydrates || 0) / totalMacros) * 100) : 0;
  const fPct = totalMacros > 0 ? Math.round(((fat || 0) / totalMacros) * 100) : 0;

  return (
    <div className="bg-white rounded-2xl border border-stone-200/80 shadow-xs p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-saffron-600">
            Estimated Nutritional Profile
          </span>
          <h2 className="text-xl font-extrabold text-charcoal-900">{food_name}</h2>
          <p className="text-xs text-stone-500 mt-0.5">
            Serving: <span className="font-semibold text-charcoal-800">{servingSize}</span> ({serving_weight_g}g)
            {serving_description && ` • ${serving_description}`}
          </p>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end space-x-1 text-saffron-600">
            <Flame className="w-5 h-5 fill-saffron-500" />
            <span className="text-2xl font-black">{calories ?? '—'}</span>
            <span className="text-xs font-bold text-stone-500">kcal</span>
          </div>
          <span className="text-[10px] text-stone-400">Total Energy</span>
        </div>
      </div>

      {/* Macronutrient Metric Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <div className="p-3.5 rounded-xl bg-amber-50/70 border border-amber-200/70">
          <div className="flex items-center space-x-1.5 text-amber-800 mb-1">
            <Wheat className="w-4 h-4" />
            <span className="text-xs font-bold">Carbohydrates</span>
          </div>
          <div className="text-lg font-black text-charcoal-900">
            {carbohydrates ?? '—'} <span className="text-xs font-semibold text-stone-500">g</span>
          </div>
          <span className="text-[10px] text-amber-700 font-medium">{cPct}% of macros</span>
        </div>

        <div className="p-3.5 rounded-xl bg-sky-50/70 border border-sky-200/70">
          <div className="flex items-center space-x-1.5 text-sky-800 mb-1">
            <Beef className="w-4 h-4" />
            <span className="text-xs font-bold">Protein</span>
          </div>
          <div className="text-lg font-black text-charcoal-900">
            {protein ?? '—'} <span className="text-xs font-semibold text-stone-500">g</span>
          </div>
          <span className="text-[10px] text-sky-700 font-medium">{pPct}% of macros</span>
        </div>

        <div className="p-3.5 rounded-xl bg-rose-50/70 border border-rose-200/70">
          <div className="flex items-center space-x-1.5 text-rose-800 mb-1">
            <Droplets className="w-4 h-4" />
            <span className="text-xs font-bold">Fat / Lipids</span>
          </div>
          <div className="text-lg font-black text-charcoal-900">
            {fat ?? '—'} <span className="text-xs font-semibold text-stone-500">g</span>
          </div>
          <span className="text-[10px] text-rose-700 font-medium">{fPct}% of macros</span>
        </div>

        <div className="p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200/70">
          <div className="flex items-center space-x-1.5 text-emerald-800 mb-1">
            <Wheat className="w-4 h-4" />
            <span className="text-xs font-bold">Dietary Fiber</span>
          </div>
          <div className="text-lg font-black text-charcoal-900">
            {fiber ?? '—'} <span className="text-xs font-semibold text-stone-500">g</span>
          </div>
          <span className="text-[10px] text-emerald-700 font-medium">Digestive</span>
        </div>
      </div>

      {/* Visual Macro Proportion Bar */}
      <div className="mb-5">
        <div className="flex justify-between text-[11px] font-semibold text-stone-500 mb-1.5">
          <span>Macronutrient Distribution</span>
          <span>Carbs ({cPct}%) • Protein ({pPct}%) • Fat ({fPct}%)</span>
        </div>
        <div className="h-2.5 w-full bg-stone-100 rounded-full overflow-hidden flex">
          <div style={{ width: `${cPct}%` }} className="bg-amber-400" title="Carbohydrates" />
          <div style={{ width: `${pPct}%` }} className="bg-sky-400" title="Protein" />
          <div style={{ width: `${fPct}%` }} className="bg-rose-400" title="Fat" />
        </div>
      </div>

      {/* Data Provenance & Scientific Citation */}
      <div className="rounded-xl bg-stone-50 border border-stone-200/80 p-4 space-y-2">
        <div className="flex items-center space-x-2 text-xs font-bold text-charcoal-900">
          <BookOpen className="w-3.5 h-3.5 text-saffron-600" />
          <span>Scientific Data Provenance</span>
        </div>
        <div className="text-[11px] text-stone-600 leading-relaxed">
          <p>
            <strong className="text-charcoal-900">Source:</strong> {data_source}
          </p>
          {source_reference && (
            <p>
              <strong className="text-charcoal-900">Reference:</strong> {source_reference}
            </p>
          )}
          {notes_uncertainty && (
            <p className="mt-1 text-stone-500 italic">
              <strong>Variation Note:</strong> {notes_uncertainty}
            </p>
          )}
        </div>

        {/* Mandatory Street Food Recipe Disclaimer */}
        <div className="pt-2 border-t border-stone-200/70 flex items-start space-x-2 text-[10px] text-amber-800">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
          <span>
            {disclaimer ||
              'Values are estimates based on standardized composite recipes. Real street food portion sizes, frying oil temperature, and butter additions vary widely between vendors.'}
          </span>
        </div>
      </div>
    </div>
  );
}
