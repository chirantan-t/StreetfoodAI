import React, { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon, Sparkles } from 'lucide-react';

export default function ImageUploader({ selectedFile, previewUrl, onImageSelected, onImageRemoved }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload a valid image file (JPEG, PNG, WebP).');
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      onImageSelected(file, event.target.result);
    };
    reader.readAsDataURL(file);
  };

  // Quick sample test loader using real high-resolution photographs
  const samples = [
    { name: 'Pav Bhaji', file: 'pav_bhaji.jpg' },
    { name: 'Vada Pav', file: 'vada_pav.jpg' },
    { name: 'Samosa', file: 'samosa.jpg' },
    { name: 'Idli', file: 'idli.jpg' },
    { name: 'Pani Puri', file: 'pani_puri.jpg' },
  ];

  const loadSampleFood = async (sample) => {
    try {
      const resp = await fetch(`/samples/${sample.file}`);
      const blob = await resp.blob();
      const file = new File([blob], sample.file, { type: 'image/jpeg' });
      const preview = URL.createObjectURL(blob);
      onImageSelected(file, preview);
    } catch (err) {
      console.error('Failed to load sample image:', err);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-stone-200/80 shadow-xs p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-charcoal-900">Upload Food Photograph</h2>
          <p className="text-xs text-stone-500">Supports JPEG, PNG, or WebP (max 10MB)</p>
        </div>
        {previewUrl && (
          <button
            onClick={onImageRemoved}
            className="flex items-center space-x-1 text-xs text-rose-600 hover:text-rose-700 bg-rose-50 px-2.5 py-1 rounded-lg border border-rose-200 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
            <span>Remove</span>
          </button>
        )}
      </div>

      {!previewUrl ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
            isDragging
              ? 'border-saffron-500 bg-saffron-50/50 scale-[0.99]'
              : 'border-stone-300 hover:border-saffron-400 bg-stone-50/40 hover:bg-stone-50'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
          />
          <div className="w-14 h-14 mx-auto mb-3 rounded-2xl bg-saffron-100/80 text-saffron-600 flex items-center justify-center shadow-xs">
            <Upload className="w-6 h-6" />
          </div>
          <p className="text-sm font-semibold text-charcoal-900 mb-1">
            Drag and drop your food photo here, or <span className="text-saffron-600 underline">browse</span>
          </p>
          <p className="text-xs text-stone-500">
            For best recognition, ensure clear lighting and centered framing on the dish.
          </p>
        </div>
      ) : (
        <div className="relative rounded-xl overflow-hidden border border-stone-200 bg-stone-900 flex items-center justify-center max-h-[380px]">
          <img
            src={previewUrl}
            alt="Uploaded Indian street food"
            className="w-full h-full object-contain max-h-[380px]"
          />
          <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md text-white text-[11px] px-2.5 py-1 rounded-md flex items-center space-x-1.5">
            <ImageIcon className="w-3.5 h-3.5" />
            <span>{selectedFile?.name || 'Selected Food Image'}</span>
          </div>
        </div>
      )}

      {/* Quick Test Samples */}
      <div className="mt-4 pt-4 border-t border-stone-100">
        <div className="flex items-center space-x-1.5 text-xs font-semibold text-stone-600 mb-2">
          <Sparkles className="w-3.5 h-3.5 text-saffron-500" />
          <span>Or test with a sample dish:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {samples.map((s) => (
            <button
              key={s.name}
              type="button"
              onClick={() => loadSampleFood(s)}
              className="text-xs font-medium px-3 py-1.5 rounded-lg bg-stone-100 hover:bg-saffron-100 text-stone-700 hover:text-saffron-800 border border-stone-200/80 transition-colors"
            >
              {s.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
