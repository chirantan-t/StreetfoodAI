import React, { useEffect, useState } from 'react';
import { Utensils, Activity, History, Info, Sparkles, BarChart2 } from 'lucide-react';
import { fetchHealth } from '../services/api';

export default function Navbar({ activeTab, setActiveTab }) {
  const [backendStatus, setBackendStatus] = useState({ online: false, model: 'Connecting...' });

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setBackendStatus({
          online: true,
          model: data.model_architecture,
          ready: data.is_model_ready,
        });
      })
      .catch(() => {
        setBackendStatus({ online: false, model: 'Offline' });
      });
  }, []);

  const navItems = [
    { id: 'home', label: 'Home', icon: Utensils },
    { id: 'recognition', label: 'Scan Food', icon: Sparkles },
    { id: 'history', label: 'Meal History', icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-stone-200/80 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div
            onClick={() => setActiveTab('home')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-saffron-600 to-amber-500 flex items-center justify-center text-white shadow-md shadow-saffron-500/20 group-hover:scale-105 transition-transform">
              <Utensils className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-extrabold text-xl tracking-tight text-charcoal-900">
                  StreetFood<span className="text-saffron-600">AI</span>
                </span>
                <span className="text-[10px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-saffron-50 text-saffron-700 border border-saffron-200">
                  Nutrition
                </span>
              </div>
              <p className="text-[11px] text-stone-500 hidden sm:block">Indian Street Food & Nutrition Tracker</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-saffron-50 text-saffron-700 shadow-xs'
                      : 'text-stone-600 hover:text-charcoal-900 hover:bg-stone-100/70'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-saffron-600' : 'text-stone-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Quick CTA */}
          <div className="hidden sm:flex items-center">
            <button
              onClick={() => setActiveTab('recognition')}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-saffron-600 hover:bg-saffron-500 text-white text-xs font-bold transition-all shadow-xs"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Scan Dish</span>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile nav row */}
      <div className="md:hidden flex overflow-x-auto py-2 px-4 space-x-2 border-t border-stone-100 bg-stone-50/60">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap ${
                isActive ? 'bg-saffron-600 text-white' : 'text-stone-600 bg-white border border-stone-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
