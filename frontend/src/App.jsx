import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Recognition from './pages/Recognition';
import Analytics from './pages/Analytics';
import History from './pages/History';
import About from './pages/About';
import { Utensils, Heart } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <Home onNavigate={(tab) => setActiveTab(tab)} />;
      case 'recognition':
        return <Recognition />;
      case 'analytics':
        return <Analytics />;
      case 'history':
        return <History />;
      case 'about':
        return <About />;
      default:
        return <Home onNavigate={(tab) => setActiveTab(tab)} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-warmbg text-charcoal-900 selection:bg-saffron-200">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-stone-200/80 py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-stone-500 gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-lg bg-saffron-500 flex items-center justify-center text-white">
              <Utensils className="w-3.5 h-3.5" />
            </div>
            <span className="font-bold text-charcoal-800">StreetFoodAI</span>
            <span>• Indian Street Food Nutrition Tracker</span>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-stone-400">ICMR-NIN IFCT 2017 Scientific Standard</span>
            <span>•</span>
            <span>Portion-Scaled Nutrition</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
