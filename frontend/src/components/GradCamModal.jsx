import React from 'react';
import { X, Eye, Info, Sparkles, AlertCircle } from 'lucide-react';

export default function GradCamModal({ isOpen, onClose, originalImageUrl, gradCamData, foodName }) {
  if (!isOpen || !gradCamData) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="relative bg-white rounded-3xl max-w-3xl w-full border border-stone-200 shadow-2xl p-6 sm:p-8 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-100 mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-saffron-100 text-saffron-600 flex items-center justify-center">
              <Eye className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-extrabold text-charcoal-900">Grad-CAM Visual Attention</h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-saffron-50 text-saffron-700 border border-saffron-200">
                  Explainable AI
                </span>
              </div>
              <p className="text-xs text-stone-500">
                Visual explanation of convolutional feature activation for{' '}
                <strong className="text-charcoal-900">{foodName || gradCamData.predicted_class}</strong>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 text-stone-600 flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Side-by-side or stacked visual comparison */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <div className="border border-stone-200 rounded-2xl overflow-hidden bg-stone-50">
            <div className="px-3 py-2 bg-white border-b border-stone-100 text-xs font-semibold text-stone-700">
              Input Photograph (Preserved)
            </div>
            <div className="h-64 flex items-center justify-center bg-stone-900">
              <img
                src={originalImageUrl}
                alt="Original food upload"
                className="w-full h-full object-contain"
              />
            </div>
          </div>

          <div className="border border-saffron-200 rounded-2xl overflow-hidden bg-stone-50">
            <div className="px-3 py-2 bg-saffron-50/80 border-b border-saffron-100 text-xs font-semibold text-saffron-900 flex items-center justify-between">
              <span>Grad-CAM Activation Heatmap</span>
              <span className="text-[10px] text-saffron-700 font-bold">Jet Colormap</span>
            </div>
            <div className="h-64 flex items-center justify-center bg-stone-900">
              <img
                src={gradCamData.heatmap_overlay_base64}
                alt="Grad-CAM activation overlay"
                className="w-full h-full object-contain"
              />
            </div>
          </div>
        </div>

        {/* Technical Details & Interpretive Disclaimer */}
        <div className="rounded-2xl bg-amber-50/70 border border-amber-200/80 p-4 space-y-2 text-xs text-amber-950">
          <div className="flex items-center space-x-2 font-bold text-amber-900">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>Research & Interpretability Disclaimer</span>
          </div>
          <p className="leading-relaxed">
            {gradCamData.disclaimer ||
              'Grad-CAM visualizes gradient attention maps of the final convolutional layer. It shows which image regions influenced the classification score, and serves as an explanatory diagnostic rather than proof of ground-truth correctness.'}
          </p>
          <div className="pt-2 border-t border-amber-200/60 flex flex-wrap gap-4 text-[11px] text-stone-600">
            <span>
              <strong>Target Layer:</strong> {gradCamData.target_layer}
            </span>
            <span>
              <strong>Activation Score:</strong> {Math.round(gradCamData.confidence * 100)}%
            </span>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-xl bg-charcoal-900 hover:bg-charcoal-800 text-white text-xs font-bold transition-colors shadow-sm"
          >
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
}
