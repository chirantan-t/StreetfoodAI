import React from 'react';
import { ArrowRight, Sparkles, Scale, ShieldCheck, Utensils, CheckCircle2 } from 'lucide-react';

export default function Home({ onNavigate }) {
  const categories = [
    'Vada Pav', 'Pav Bhaji', 'Misal Pav', 'Pani Puri', 'Bhel Puri',
    'Sev Puri', 'Dabeli', 'Samosa', 'Kachori', 'Dosa',
    'Idli', 'Medu Vada', 'Poha', 'Upma', 'Chole Bhature',
    'Aloo Tikki', 'Frankie', 'Sandwich', 'Jalebi'
  ];

  return (
    <div className="space-y-12 py-6">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-charcoal-900 via-charcoal-950 to-stone-900 text-white p-8 sm:p-12 border border-stone-800 shadow-xl">
        <div className="relative z-10 max-w-3xl space-y-5">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-saffron-500/10 border border-saffron-500/30 text-saffron-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Instant Food Identification & Nutrition</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
            Know What You Eat: <span className="text-saffron-500">Street Food Nutrition</span>
          </h1>

          <p className="text-stone-300 text-sm sm:text-base leading-relaxed">
            Snap or upload a photo of your favorite Indian street food dish. Get instant calorie counts and macronutrient breakdowns scientifically verified by official ICMR-NIN composition standards.
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <button
              onClick={() => onNavigate('recognition')}
              className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-saffron-600 hover:bg-saffron-500 text-white font-bold text-sm transition-all shadow-lg shadow-saffron-600/30 hover:scale-105"
            >
              <span>Scan Your Meal</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('history')}
              className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-white/10 hover:bg-white/15 text-stone-200 border border-white/10 font-semibold text-sm transition-colors"
            >
              <span>View Past Meals</span>
            </button>
          </div>
        </div>

        {/* Ambient background blur accent */}
        <div className="absolute -right-20 -bottom-20 w-96 h-96 bg-saffron-600/20 rounded-full blur-3xl pointer-events-none" />
      </section>

      {/* How It Works - Consumer Friendly */}
      <section className="space-y-4">
        <div className="text-center max-w-2xl mx-auto mb-8">
          <h2 className="text-2xl font-extrabold text-charcoal-900">How It Works</h2>
          <p className="text-xs text-stone-500 mt-1">
            Simple, fast, and scientifically grounded dietary tracking in three steps.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-6 border border-stone-200/80 shadow-xs space-y-3">
            <div className="w-12 h-12 rounded-xl bg-saffron-50 text-saffron-600 flex items-center justify-center">
              <Utensils className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-charcoal-900">1. Upload a Photo</h3>
            <p className="text-xs text-stone-600 leading-relaxed">
              Take a quick picture of your plate or choose a photo from your gallery.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-stone-200/80 shadow-xs space-y-3">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-charcoal-900">2. Instant Recognition</h3>
            <p className="text-xs text-stone-600 leading-relaxed">
              The dish is identified with high accuracy, from Pav Bhaji and Vada Pav to Dosa and Chole Bhature.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-stone-200/80 shadow-xs space-y-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Scale className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-charcoal-900">3. Portion-Scaled Nutrition</h3>
            <p className="text-xs text-stone-600 leading-relaxed">
              Select Small, Regular, or Large servings to see exact calories, protein, carbs, fat, and fiber.
            </p>
          </div>
        </div>
      </section>

      {/* Supported Dishes */}
      <section className="bg-white rounded-3xl border border-stone-200/80 p-8 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 pb-4 border-b border-stone-100">
          <div>
            <h2 className="text-xl font-bold text-charcoal-900">Popular Street Foods Supported</h2>
            <p className="text-xs text-stone-500 mt-0.5">Verified with official ICMR-NIN Indian Food Composition Tables</p>
          </div>
          <button
            onClick={() => onNavigate('recognition')}
            className="text-xs font-bold text-saffron-600 hover:text-saffron-700 mt-2 sm:mt-0 flex items-center space-x-1"
          >
            <span>Scan a Dish</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-3">
          {categories.map((cat) => (
            <div
              key={cat}
              onClick={() => onNavigate('recognition')}
              className="p-3.5 rounded-xl text-center border bg-warmbg/60 border-stone-200/80 hover:border-saffron-400 hover:bg-saffron-50/50 hover:shadow-xs transition-all cursor-pointer group"
            >
              <span className="text-xs font-bold text-charcoal-900 group-hover:text-saffron-700 transition-colors block">
                {cat}
              </span>
              <span className="text-[10px] text-stone-400 mt-0.5 block">Tap to Scan</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
