import React from 'react';
import { BookOpen, Scale, Eye, Cpu, AlertTriangle, Layers, Award } from 'lucide-react';

export default function About() {
  return (
    <div className="max-w-4xl mx-auto space-y-10 py-4">
      <div>
        <h1 className="text-3xl font-extrabold text-charcoal-900 tracking-tight">
          Scientific Methodology & Architecture
        </h1>
        <p className="text-xs text-stone-500 mt-1">
          Technical specifications, composition provenance, and research disclaimers for StreetFoodAI.
        </p>
      </div>

      {/* Problem Formulation */}
      <section className="bg-white rounded-3xl border border-stone-200/80 p-8 shadow-xs space-y-4">
        <div className="flex items-center space-x-2.5 text-saffron-600">
          <BookOpen className="w-5 h-5" />
          <h2 className="text-lg font-bold text-charcoal-900">1. Problem Formulation</h2>
        </div>
        <p className="text-xs text-stone-700 leading-relaxed">
          Indian street food poses acute challenges for computer vision and nutritional estimation: high visual intra-class variance
          (e.g., regional variations of Pav Bhaji or Misal Pav), irregular plating geometry, deep-frying lipid uptake, and overlapping garnish layers (farsan, sev, coriander, chutneys).
          Standard generic Western food datasets (e.g. Food-101) lack coverage of South Asian snacks. StreetFoodAI addresses this by uniting:
        </p>
        <ul className="list-disc list-inside text-xs text-stone-600 space-y-1.5 pl-2">
          <li>A 20-category taxonomy structured for regional Indian street snacks and sweets.</li>
          <li>Comparative deep learning across MobileNetV3-Large, EfficientNet-B0, and Zero-Shot CLIP.</li>
          <li>Transparent visual attention verification using gradient-weighted class activation mapping (Grad-CAM).</li>
          <li>Portion-scaled nutritional mapping grounded in the Indian Food Composition Tables (IFCT 2017, ICMR-NIN).</li>
        </ul>
      </section>

      {/* Model Architectures & Transfer Learning */}
      <section className="bg-white rounded-3xl border border-stone-200/80 p-8 shadow-xs space-y-4">
        <div className="flex items-center space-x-2.5 text-sky-600">
          <Cpu className="w-5 h-5" />
          <h2 className="text-lg font-bold text-charcoal-900">2. Evaluated Neural Architectures</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200/80 space-y-2">
            <h3 className="text-xs font-bold text-charcoal-900">MobileNetV3-Large</h3>
            <p className="text-[11px] text-stone-600 leading-relaxed">
              4.23M parameters. Optimized for edge and mobile deployments using hard-swish non-linearities and squeeze-and-excitation blocks. Achieves 13.5ms CPU latency.
            </p>
          </div>
          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200/80 space-y-2">
            <h3 className="text-xs font-bold text-charcoal-900">EfficientNet-B0</h3>
            <p className="text-[11px] text-stone-600 leading-relaxed">
              4.03M parameters. Uses compound scaling across depth, width, and resolution. Compact 15.4MB memory footprint with strong feature representation.
            </p>
          </div>
          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200/80 space-y-2">
            <h3 className="text-xs font-bold text-charcoal-900">CLIP Zero-Shot (ViT-B/32)</h3>
            <p className="text-[11px] text-stone-600 leading-relaxed">
              151.3M parameters. Uses joint image-text contrastive embeddings with prompt engineering templates. Evaluated without fine-tuning as a foundation baseline.
            </p>
          </div>
        </div>
      </section>

      {/* Explainable AI (Grad-CAM) */}
      <section className="bg-white rounded-3xl border border-stone-200/80 p-8 shadow-xs space-y-4">
        <div className="flex items-center space-x-2.5 text-amber-600">
          <Eye className="w-5 h-5" />
          <h2 className="text-lg font-bold text-charcoal-900">3. Explainable AI: Grad-CAM Formulation</h2>
        </div>
        <p className="text-xs text-stone-700 leading-relaxed">
          Grad-CAM computes the gradient of the class score <span className="font-mono text-saffron-700">y^c</span> with respect to feature activation map <span className="font-mono text-saffron-700">A^k</span> of the final convolutional layer:
        </p>
        <div className="p-4 rounded-xl bg-stone-900 text-stone-200 font-mono text-xs text-center border border-stone-800">
          {"α_k^c = (1 / Z) * Σ_i Σ_j (∂y^c / ∂A_ij^k)   |   L_Grad-CAM^c = ReLU(Σ_k α_k^c A^k)"}
        </div>
        <p className="text-xs text-stone-600 leading-relaxed">
          The resulting 2D attention map is normalized, upsampled to input resolution (224x224), and blended via OpenCV Jet colormap. This allows practitioners to verify whether the model is focusing on characteristic dish textures (e.g. sev garnish, pav bread, potato patties) rather than background plate clutter.
        </p>
      </section>

      {/* Nutrition Data Provenance */}
      <section className="bg-white rounded-3xl border border-stone-200/80 p-8 shadow-xs space-y-4">
        <div className="flex items-center space-x-2.5 text-emerald-600">
          <Scale className="w-5 h-5" />
          <h2 className="text-lg font-bold text-charcoal-900">4. Nutritional Provenance & Portions</h2>
        </div>
        <p className="text-xs text-stone-700 leading-relaxed">
          Macronutrient and caloric estimations are grounded in the <strong>Indian Food Composition Tables 2017 (IFCT 2017)</strong>,
          published by the National Institute of Nutrition (ICMR-NIN), Hyderabad. Three serving sizes are modeled:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-200/60">
            <strong className="text-emerald-900 block mb-1">Small Serving</strong>
            <p className="text-stone-600">Single piece, half pav, or reduced street portion (~60-220g).</p>
          </div>
          <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-200/60">
            <strong className="text-emerald-900 block mb-1">Regular Serving</strong>
            <p className="text-stone-600">Standard vendor plate serving (1.0x baseline reference weight).</p>
          </div>
          <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-200/60">
            <strong className="text-emerald-900 block mb-1">Large Serving</strong>
            <p className="text-stone-600">Extra pav, double snack piece, or jumbo portion (1.4x-1.5x scaling).</p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start space-x-2.5 mt-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong>Vendor Variance Notice:</strong> Real street food values are subject to substantial vendor-level variance due to differing oil frying temperatures, batter thickness, and butter/ghee finishing. Exact calorie counts cannot be derived from pixels alone.
          </p>
        </div>
      </section>

      {/* Limitations & Future Work */}
      <section className="bg-white rounded-3xl border border-stone-200/80 p-8 shadow-xs space-y-4">
        <div className="flex items-center space-x-2.5 text-purple-600">
          <Layers className="w-5 h-5" />
          <h2 className="text-lg font-bold text-charcoal-900">5. Research Limitations & Future Roadmap</h2>
        </div>
        <ul className="list-disc list-inside text-xs text-stone-600 space-y-2 pl-2">
          <li><strong>Out-of-Distribution Calibration:</strong> Softmax scores on unrecognized food are flagged via entropy and confidence thresholds, but true zero-shot out-of-distribution detection remains an active research direction.</li>
          <li><strong>Instance Segmentation:</strong> Future iterations will integrate Mask R-CNN or YOLOv8-seg for separating multiple distinct food items present on a single thali or chaat counter.</li>
          <li><strong>Reference-Object 3D Depth:</strong> Integrating coin or hand fiducial markers for volumetric portion estimation rather than user-selected categorical servings.</li>
        </ul>
      </section>
    </div>
  );
}
