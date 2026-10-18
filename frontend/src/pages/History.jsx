import React, { useEffect, useState } from 'react';
import { History as HistoryIcon, Trash2, Calendar, Flame, RefreshCw, AlertCircle, Scale } from 'lucide-react';
import { fetchHistory, deleteHistory } from '../services/api';

export default function History() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadHistory = () => {
    setLoading(true);
    fetchHistory()
      .then((data) => {
        setRecords(data);
        setError(null);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load history.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete prediction record #${id}?`)) return;
    try {
      await deleteHistory(id);
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 py-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900 tracking-tight">
            Meal & Dietary History
          </h1>
          <p className="text-xs text-stone-500 mt-1">
            Your personal log of scanned meals, portions, and estimated macronutrients.
          </p>
        </div>
        <button
          onClick={loadHistory}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs font-semibold self-start sm:self-auto transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-stone-200">
          <div className="w-8 h-8 border-4 border-saffron-200 border-t-saffron-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-stone-500">Loading saved records...</p>
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      ) : records.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-dashed border-stone-300 space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-stone-100 text-stone-400 mx-auto flex items-center justify-center">
            <HistoryIcon className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-charcoal-800">No Prediction History Yet</h3>
          <p className="text-xs max-w-sm mx-auto text-stone-500">
            When you recognize a food item and click "Save Record", it will appear here with its portion and macronutrient estimates.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-stone-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-stone-50 border-b border-stone-100 text-stone-500 uppercase font-semibold">
                <tr>
                  <th className="px-6 py-4">Food Item</th>
                  <th className="px-6 py-4">Date & Time</th>
                  <th className="px-6 py-4">Serving Portion</th>
                  <th className="px-6 py-4">Calories</th>
                  <th className="px-6 py-4">Carbs</th>
                  <th className="px-6 py-4">Protein</th>
                  <th className="px-6 py-4">Fat</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 text-charcoal-900">
                {records.map((r) => {
                  const dateStr = r.timestamp
                    ? new Date(r.timestamp).toLocaleString(undefined, {
                        dateStyle: 'medium',
                        timeStyle: 'short',
                      })
                    : '—';
                  return (
                    <tr key={r.id} className="hover:bg-stone-50/60 transition-colors">
                      <td className="px-6 py-4 font-bold text-charcoal-900">
                        <div className="flex items-center space-x-2">
                          <span>{r.food_name}</span>
                          {r.is_uncertain && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] bg-amber-100 text-amber-800 font-semibold">
                              Uncertain
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-stone-500 whitespace-nowrap">{dateStr}</td>
                      <td className="px-6 py-4">
                        <span className="font-semibold text-stone-700">{r.serving_size}</span>
                        {r.serving_weight_g && (
                          <span className="text-[10px] text-stone-400 block">{r.serving_weight_g}g</span>
                        )}
                      </td>
                      <td className="px-6 py-4 font-bold text-saffron-600">
                        {r.calories != null ? `${r.calories} kcal` : '—'}
                      </td>
                      <td className="px-6 py-4 text-stone-600">
                        {r.carbohydrates != null ? `${r.carbohydrates}g` : '—'}
                      </td>
                      <td className="px-6 py-4 text-stone-600">
                        {r.protein != null ? `${r.protein}g` : '—'}
                      </td>
                      <td className="px-6 py-4 text-stone-600">
                        {r.fat != null ? `${r.fat}g` : '—'}
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Logged
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleDelete(r.id)}
                          className="p-1.5 rounded-lg text-stone-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Delete record"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
