import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Bookmark,
  Check,
  RefreshCw,
  AlertCircle,
  Utensils,
  Eye,
  CheckCircle2,
  AlertTriangle,
  ChevronDown
} from 'lucide-react';
import ImageUploader from '../components/ImageUploader';
import ServingSelector from '../components/ServingSelector';
import NutritionCard from '../components/NutritionCard';
import UnknownFoodAlert from '../components/UnknownFoodAlert';
import GradCamModal from '../components/GradCamModal';
import {
  predictImage,
  fetchFoodNutrition,
  saveHistory,
  fetchSupportedFoods,
  explainImage
} from '../services/api';

export default function Recognition() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [servingSize, setServingSize] = useState('Regular');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prediction, setPrediction] = useState(null);

  // Supported foods list
  const [supportedFoods, setSupportedFoods] = useState([]);

  // Grad-CAM modal state
  const [isGradCamOpen, setIsGradCamOpen] = useState(false);
  const [gradCamData, setGradCamData] = useState(null);
  const [isExplaining, setIsExplaining] = useState(false);

  // History save state
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    fetchSupportedFoods()
      .then((data) => {
        if (!data) return;
        if (Array.isArray(data)) {
          setSupportedFoods(data);
        } else if (data.foods && typeof data.foods === 'object') {
          const list = Object.keys(data.foods).map((name) => ({
            name,
            ...(typeof data.foods[name] === 'object' ? data.foods[name] : {})
          }));
          setSupportedFoods(list);
        } else {
          setSupportedFoods([]);
        }
      })
      .catch((err) => console.warn('Could not load supported foods list:', err));
  }, []);

  const handleImageSelected = (file, dataUrl) => {
    setSelectedFile(file);
    setPreviewUrl(dataUrl);
    setPrediction(null);
    setError(null);
    setIsSaved(false);
    setGradCamData(null);
  };

  const handleImageRemoved = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setPrediction(null);
    setError(null);
    setIsSaved(false);
    setGradCamData(null);
  };

  const handleRunPrediction = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);
    setIsSaved(false);
    setGradCamData(null);

    try {
      const result = await predictImage(selectedFile, servingSize);
      setPrediction(result);
    } catch (err) {
      setError(err.message || 'Failed to analyze meal image.');
    } finally {
      setIsLoading(false);
    }
  };

  // Re-fetch nutrition when portion size changes
  const handleServingChange = async (newServing) => {
    setServingSize(newServing);
    if (prediction && prediction.predicted_food) {
      try {
        const nutData = await fetchFoodNutrition(prediction.predicted_food, newServing);
        setPrediction((prev) => ({
          ...prev,
          serving_size: newServing,
          nutrition: nutData,
        }));
      } catch (err) {
        console.error('Failed to update portion nutrition:', err);
      }
    }
  };

  // User selects candidate or manual change
  const handleSelectCandidate = async (dishName) => {
    try {
      const nutData = await fetchFoodNutrition(dishName, servingSize);
      setPrediction((prev) => ({
        ...prev,
        predicted_food: dishName,
        is_uncertain: false,
        rejection_reason: null,
        nutrition: nutData,
      }));
    } catch (err) {
      console.error('Candidate selection failed:', err);
    }
  };

  // Explain with Grad-CAM
  const handleExplainMeal = async () => {
    if (!selectedFile || !prediction) return;
    setIsExplaining(true);
    try {
      const data = await explainImage(selectedFile, prediction.predicted_class_index);
      setGradCamData(data);
      setIsGradCamOpen(true);
    } catch (err) {
      alert(`Grad-CAM explanation failed: ${err.message}`);
    } finally {
      setIsExplaining(false);
    }
  };

  // Save to history
  const handleSaveToHistory = async () => {
    if (!prediction || isSaved) return;
    setIsSaving(true);
    try {
      await saveHistory({
        food_name: prediction.predicted_food,
        confidence: prediction.confidence,
        serving_size: servingSize,
        serving_weight_g: prediction.nutrition?.serving_weight_g,
        calories: prediction.nutrition?.calories,
        protein: prediction.nutrition?.protein,
        carbohydrates: prediction.nutrition?.carbohydrates,
        fat: prediction.nutrition?.fat,
        fiber: prediction.nutrition?.fiber,
        is_uncertain: prediction.is_uncertain,
        model_architecture: prediction.model_architecture,
        notes: `Analyzed portion: ${servingSize}`,
      });
      setIsSaved(true);
    } catch (err) {
      alert(`Failed to save record: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const isIdentified = prediction && !prediction.is_uncertain;

  return (
    <div className="space-y-8 py-4">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900 tracking-tight">
          Scan & Analyze Meal
        </h1>
        <p className="text-xs text-stone-500 mt-1">
          Upload a photograph of your street food dish for instant, portion-scaled nutritional estimation.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Image Uploader & Controls */}
        <div className="lg:col-span-5 space-y-5">
          <ImageUploader
            selectedFile={selectedFile}
            previewUrl={previewUrl}
            onImageSelected={handleImageSelected}
            onImageRemoved={handleImageRemoved}
          />

          {previewUrl && (
            <div className="flex flex-col space-y-3">
              <button
                type="button"
                onClick={handleRunPrediction}
                disabled={isLoading}
                className={`w-full py-3.5 px-6 rounded-2xl font-bold text-sm text-white flex items-center justify-center space-x-2 transition-all shadow-md ${
                  isLoading
                    ? 'bg-stone-400 cursor-not-allowed'
                    : 'bg-saffron-600 hover:bg-saffron-500 shadow-saffron-600/30 hover:scale-[1.01]'
                }`}
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing Meal...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Analyze Nutrition</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Error Banner */}
          {error && (
            <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-2.5">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">Analysis Notice</p>
                <p className="mt-0.5 text-stone-600">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Results & Nutrition */}
        <div className="lg:col-span-7 space-y-6">
          {!prediction && !isLoading && (
            <div className="bg-white rounded-3xl border border-dashed border-stone-300 p-12 text-center text-stone-400 space-y-3">
              <div className="w-16 h-16 rounded-2xl bg-stone-100 mx-auto flex items-center justify-center text-stone-400">
                <Utensils className="w-8 h-8 text-stone-400" />
              </div>
              <h3 className="text-base font-bold text-charcoal-800">Ready to Scan Meal</h3>
              <p className="text-xs max-w-sm mx-auto text-stone-500">
                Upload or select a dish on the left, then click <strong>"Analyze Nutrition"</strong> to calculate verified calories and macronutrients.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="bg-white rounded-3xl border border-stone-200/80 p-12 text-center space-y-4 shadow-xs">
              <div className="w-12 h-12 rounded-full border-4 border-saffron-200 border-t-saffron-600 animate-spin mx-auto" />
              <p className="text-sm font-bold text-charcoal-900">Identifying Dish & Calculating Nutrition...</p>
              <p className="text-xs text-stone-500">
                Cross-referencing food composition data from the National Institute of Nutrition (ICMR-NIN).
              </p>
            </div>
          )}

          {prediction && !isLoading && (
            <div className="space-y-6">
              {/* Fallback suggestion if low confidence / out of distribution */}
              <UnknownFoodAlert
                prediction={prediction}
                onSelectCandidate={handleSelectCandidate}
              />

              {/* Identified Dish Card */}
              {isIdentified && (
                <div className="bg-white rounded-2xl border border-stone-200/80 shadow-xs p-6 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-[11px] font-bold text-saffron-600 uppercase tracking-wider bg-saffron-50 px-2.5 py-0.5 rounded-full border border-saffron-200/80">
                          Identified Dish
                        </span>

                        {/* Match Confidence Badge */}
                        {prediction.confidence >= 0.70 ? (
                          <span className="inline-flex items-center space-x-1 text-[11px] font-bold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                            <span>{Math.round(prediction.confidence * 100)}% Match</span>
                          </span>
                        ) : prediction.confidence >= 0.45 ? (
                          <span className="inline-flex items-center space-x-1 text-[11px] font-bold text-amber-800 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                            <AlertTriangle className="w-3 h-3 text-amber-600" />
                            <span>{Math.round(prediction.confidence * 100)}% Match (Review)</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 text-[11px] font-bold text-rose-800 bg-rose-50 px-2.5 py-0.5 rounded-full border border-rose-200">
                            <AlertCircle className="w-3 h-3 text-rose-600" />
                            <span>{Math.round(prediction.confidence * 100)}% Match (Low)</span>
                          </span>
                        )}
                      </div>

                      <h2 className="text-3xl font-black text-charcoal-900 mt-1.5">
                        {prediction.predicted_food}
                      </h2>
                    </div>

                    <div className="flex items-center space-x-2 shrink-0">
                      {/* Explainability button */}
                      <button
                        type="button"
                        onClick={handleExplainMeal}
                        disabled={isExplaining}
                        className="flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-bold text-saffron-700 bg-saffron-50 hover:bg-saffron-100 border border-saffron-200 transition-all cursor-pointer shadow-2xs"
                        title="View convolutional activation heatmap"
                      >
                        <Eye className="w-3.5 h-3.5 text-saffron-600" />
                        <span>{isExplaining ? 'Computing...' : 'AI Attention'}</span>
                      </button>

                      {/* Save to history */}
                      <button
                        type="button"
                        onClick={handleSaveToHistory}
                        disabled={isSaved || isSaving}
                        className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                          isSaved
                            ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                            : 'bg-stone-100 hover:bg-stone-200 text-stone-800 shadow-2xs'
                        }`}
                      >
                        {isSaved ? (
                          <>
                            <Check className="w-4 h-4 text-emerald-600" />
                            <span>Saved to Log</span>
                          </>
                        ) : (
                          <>
                            <Bookmark className="w-4 h-4" />
                            <span>{isSaving ? 'Saving...' : 'Save to Log'}</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Alternative candidate buttons & quick selector */}
                  <div className="pt-3 border-t border-stone-100 flex flex-wrap items-center gap-2">
                    <span className="text-[11px] font-semibold text-stone-500">Other possibilities:</span>
                    {prediction.top_candidates
                      ?.filter(
                        (c) =>
                          c.food_name !== prediction.predicted_food &&
                          !c.food_name.toLowerCase().includes('unknown')
                      )
                      .slice(0, 3)
                      .map((candidate) => (
                        <button
                          key={candidate.class_index}
                          type="button"
                          onClick={() => handleSelectCandidate(candidate.food_name)}
                          className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-stone-100 hover:bg-saffron-50 hover:text-saffron-900 hover:border-saffron-300 border border-stone-200 text-stone-700 transition-all cursor-pointer shadow-2xs"
                        >
                          <span>{candidate.food_name}</span>
                          <span className="text-[10px] text-stone-400 font-mono">
                            {Math.round(candidate.confidence * 100)}%
                          </span>
                        </button>
                      ))}

                    {/* Change dish selector */}
                    <div className="ml-auto flex items-center space-x-1.5">
                      <span className="text-[11px] text-stone-400">or change:</span>
                      <select
                        value={prediction.predicted_food}
                        onChange={(e) => handleSelectCandidate(e.target.value)}
                        className="text-xs font-semibold bg-stone-50 hover:bg-stone-100 border border-stone-200 rounded-lg px-2 py-1 text-stone-700 cursor-pointer focus:ring-1 focus:ring-saffron-500"
                      >
                        <option value="" disabled>Select food...</option>
                        {supportedFoods.map((f) => (
                          <option key={f.name} value={f.name}>
                            {f.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Portion Selector & Nutrition Card only when dish is identified */}
              {isIdentified && (
                <>
                  <ServingSelector
                    currentServing={servingSize}
                    onServingChange={handleServingChange}
                    servingWeightG={prediction.nutrition?.serving_weight_g}
                  />

                  <NutritionCard
                    nutrition={prediction.nutrition}
                    servingSize={servingSize}
                  />
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Grad-CAM Modal */}
      <GradCamModal
        isOpen={isGradCamOpen}
        onClose={() => setIsGradCamOpen(false)}
        originalImageUrl={previewUrl}
        gradCamData={gradCamData}
        foodName={prediction?.predicted_food}
      />
    </div>
  );
}
