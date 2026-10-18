import React from 'react';
import { HelpCircle, ChevronRight } from 'lucide-react';

export default function UnknownFoodAlert({ prediction, onSelectCandidate }) {
  if (!prediction || !prediction.is_uncertain) return null;

  const validCandidates = prediction.top_candidates
    ?.filter((c) => !c.food_name.toLowerCase().includes('unknown'))
    .slice(0, 4) || [];

  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50/90 p-5 shadow-xs mb-6">
      <div className="flex items-start space-x-3.5">
        <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
          <HelpCircle className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h4 className="text-sm font-bold text-amber-950">Could not clearly match this dish</h4>
          </div>

          <p className="text-xs text-amber-900/80 mt-1 leading-relaxed">
            Angles, lighting, or garnishes can make recognition challenging. Did your dish look like one of these?
          </p>

          {validCandidates.length > 0 && (
            <div className="mt-3">
              <span className="text-[11px] font-semibold text-amber-800 block mb-2">
                Select your dish to view verified nutrition:
              </span>
              <div className="flex flex-wrap gap-2">
                {validCandidates.map((candidate) => (
                  <button
                    key={candidate.class_index}
                    type="button"
                    onClick={() => onSelectCandidate(candidate.food_name)}
                    className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-white hover:bg-amber-100/90 text-amber-950 border border-amber-200 text-xs font-semibold transition-all shadow-2xs hover:scale-[1.02] cursor-pointer"
                  >
                    <span>{candidate.food_name}</span>
                    <span className="text-[10px] text-amber-700/70 font-mono">
                      ({Math.round(candidate.confidence * 100)}%)
                    </span>
                    <ChevronRight className="w-3.5 h-3.5 text-amber-600" />
                  </button>
                ))}
              </div>
            </div>
          )}

          <p className="text-[11px] text-stone-500 mt-3">
            Tip: You can also re-upload a photo with centered framing and clearer lighting.
          </p>
        </div>
      </div>
    </div>
  );
}
