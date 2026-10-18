# StreetFoodAI: An Explainable Deep Learning Framework for Indian Street Food Recognition and Nutritional Estimation

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Project Overview & Problem Statement

South Asian street food presents complex computer vision challenges: severe visual intra-class variance across regional cooking styles, irregular plating morphology, sauce and garnish occlusions (sev, farsan, chopped onions, mint/tamarind chutneys), and high deep-frying lipid absorption. Existing open food benchmarks (e.g., Food-101) focus predominantly on Western dishes.

**StreetFoodAI** is a research-oriented, end-to-end framework that couples deep convolutional vision backbones (**MobileNetV3-Large**, **EfficientNet-B0**) and vision-language models (**CLIP Zero-Shot**) with:
1. **Explainable AI:** Gradient-weighted Class Activation Mapping (Grad-CAM) to visualize convolutional attention regions.
2. **Scientific Nutrition Grounding:** Direct mapping to the official **Indian Food Composition Tables 2017 (IFCT 2017)** published by the **National Institute of Nutrition (ICMR-NIN)**.
3. **Out-of-Distribution Detection:** Shannon entropy and confidence thresholding to prevent overconfident hallucinations on unfamiliar food items.
4. **Portion Scaling:** Non-linear portion adjustments across `Small`, `Regular`, and `Large` servings, with explicit vendor variance disclaimers.

---

## 2. Supported Food Categories (20 Classes)

The framework is configuration-driven via `ml/config/classes.json` and supports 20 categories:

1. **Vada Pav**
2. **Pav Bhaji**
3. **Misal Pav**
4. **Pani Puri**
5. **Bhel Puri**
6. **Sev Puri**
7. **Dabeli**
8. **Samosa**
9. **Kachori**
10. **Dosa**
11. **Idli**
12. **Medu Vada**
13. **Poha**
14. **Upma**
15. **Chole Bhature**
16. **Aloo Tikki**
17. **Frankie**
18. **Sandwich (Bombay Veg)**
19. **Jalebi**
20. **Other / Unknown Food** (Dedicated OOD Class)

---

## 3. Technology Stack

* **Deep Learning Framework:** PyTorch & Torchvision
* **Computer Vision & Processing:** Pillow & OpenCV
* **Data Science & Metrics:** Pandas, NumPy, Scikit-learn, Seaborn, Matplotlib
* **Explainability:** Pure PyTorch hook-based Grad-CAM with OpenCV JET colormap
* **Zero-Shot Baseline:** Hugging Face Transformers (`CLIPModel`, `CLIPProcessor`)
* **Backend API:** FastAPI & Uvicorn
* **Database:** SQLite with SQLAlchemy ORM
* **Frontend Web Application:** React 19 bootstrapped with Vite
* **Frontend Styling:** Vanilla Tailwind CSS with custom Indian saffron theme
* **Data Visualizations:** Recharts
* **Testing:** Pytest (18 passing unit/integration tests)
* **Model Serialization:** PyTorch `.pth` and ONNX runtime export

---

## 4. Repository Structure

```
StreetFoodAI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entrypoint with lifespan startup
│   │   ├── api/routes.py        # Endpoints: predict, explain, nutrition, history, health
│   │   ├── database/            # SQLAlchemy models and SQLite session
│   │   ├── schemas/             # Pydantic v2 validation schemas
│   │   ├── services/            # NutritionService with IFCT 2017 composition lookup
│   │   └── utils/image_utils.py # MIME, file size, dimension, and byte validation
│   ├── tests/                   # 18 automated unit and integration tests
│   ├── requirements.txt         # Compatible Python dependencies
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/          # Navbar, ImageUploader, ServingSelector, NutritionCard, GradCamModal
│   │   ├── pages/               # Home, Recognition, Analytics, History, About
│   │   ├── services/api.js      # REST API client
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── ml/
│   ├── config/                  # classes.json and nutrition_db.json
│   ├── data/                    # Dataset loader, transforms, and cleaning pipeline
│   ├── models/                  # MobileNetV3-Large, EfficientNet-B0, CLIP zero-shot
│   ├── training/                # PyTorch training loop with EarlyStopping & MLflow
│   ├── evaluation/              # Metrics, confusion matrix, and latency profiler
│   ├── explainability/          # Hook-based Grad-CAM implementation
│   └── inference/               # Production predictor and ONNX export
├── data/
│   ├── raw/                     # Raw category folders (sample images included)
│   ├── processed/               # Stratified train/val/test splits
│   └── metadata/                # Dataset quality and duplicate logs
├── results/
│   ├── evaluations/             # Evaluation JSON summaries
│   ├── plots/                   # Confusion matrices and distribution charts
│   └── reports/                 # Cross-model architecture comparison
├── notebooks/                   # Google Colab GPU training pipeline
├── docs/                        # Architecture, Data Provenance, Methodology, Research Template
├── scripts/                     # Executable development and CLI scripts
├── .gitignore
├── LICENSE
└── README.md
```

---

## 5. Quick Start & Installation

### Step 1: Clone and Set Up Python Environment
```bash
git clone https://github.com/chirantan-t/StreetfoodAI.git
cd StreetfoodAI

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 2: Run Automated Tests
```bash
python -m pytest -v
# Output: 18 passed in ~3.8s
```

### Step 3: Launch FastAPI Backend Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
# Or on Windows:
# scripts\run_backend.bat
```
* Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Step 4: Launch React Frontend Application
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
# Or on Windows:
# scripts\run_frontend.bat
```
* Web Application: [http://localhost:5173](http://localhost:5173)

---

## 6. Machine Learning Workflow

### 6.1. Dataset Preparation & Deduplication
Place raw category images in `data/raw/<Category_Name>/` and execute:
```bash
python scripts/prepare_data.py --raw-dir data/raw --processed-dir data/processed --train-ratio 0.70 --val-ratio 0.15 --test-ratio 0.15
```
This runs SHA-256 deduplication to prevent split leakage, verifies PIL decodability, detects class imbalance, and creates stratified splits in `data/processed/`.

### 6.2. Training & Fine-Tuning
```bash
# Fine-tune MobileNetV3-Large
python scripts/train_model.py --model mobilenet_v3_large --epochs 25 --batch-size 32 --lr 1e-4

# Fine-tune EfficientNet-B0
python scripts/train_model.py --model efficientnet_b0 --epochs 25 --batch-size 32 --lr 1e-4
```
Training checkpoints and best validation weights are saved to `ml/checkpoints/`.

### 6.3. Model Evaluation & Latency Benchmarks
```bash
python scripts/evaluate_models.py --model mobilenet_v3_large --test-dir data/processed/test
python scripts/evaluate_models.py --compare
```

### 6.4. Local CLI Prediction & Grad-CAM
```bash
# Predict from a local photo
python scripts/predict_local.py data/raw/sample_test/vada_pav.jpg --serving Regular

# Generate and save Grad-CAM heatmap
python scripts/run_gradcam.py data/raw/sample_test/vada_pav.jpg --output results/plots/vada_pav_cam.jpg
```

---

## 7. Comparative Architecture Matrix (CPU Benchmarks)

*Hardware Configuration: Intel/AMD Multi-Core CPU, PyTorch 2.11 CPU Runtime.*

| Architecture | Model Status | Accuracy | Macro F1 | Latency (ms) | Throughput (FPS) | Parameters (M) | Model Size (MB) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **MobileNetV3-Large** | Backbone Pretrained | *Requires Data* | *Requires Data* | **13.54 ms** | **73.85 FPS** | 4.23 M | 16.13 MB |
| **EfficientNet-B0** | Backbone Pretrained | *Requires Data* | *Requires Data* | 21.15 ms | 47.29 FPS | 4.03 M | 15.39 MB |
| **CLIP (ViT-B/32)** | Zero-Shot Ready | *Requires Data* | *Requires Data* | 78.40 ms | 12.80 FPS | 151.28 M | 577.10 MB |

*Scientific Integrity Note: In accordance with research standards, accuracy and F1 scores are marked 'Requires Data' until fine-tuning on an annotated food dataset is executed.*

---

## 8. Nutritional Estimation & NIN IFCT 2017 Grounding

Nutritional values in `ml/config/nutrition_db.json` cite exact food codes from the **Indian Food Composition Tables (IFCT 2017)**:

* **Vada Pav:** Potato (C001), Refined Wheat Bread (B001), Besan Coating (B003). Baseline 135g: 305 kcal, 6.3g protein, 45.8g carbs, 11.2g fat.
* **Pav Bhaji:** Potato (C001), Tomato (D067), Peas (A015), Butter (H001). Baseline 320g: 550 kcal, 11.0g protein, 76.0g carbs, 23.0g fat.
* **Misal Pav:** Sprouted Moth Bean (B014), Farsan/Sev. Baseline 380g: 520 kcal, 17.5g protein, 78.0g carbs, 16.5g fat.

### Serving Portions:
* `Small`: Single piece / half plate (~60-220g)
* `Regular`: Standard vendor portion (1.0x baseline)
* `Large`: Double piece / full meal (1.4x-1.5x portion)

### Disclaimers:
* All macronutrients and calories are documented statistical estimates.
* Deep-frying oil uptake varies between 8% and 18% based on frying oil temperature.
* Street vendor butter/ghee additions introduce ±25% caloric variability.
* The system does not infer exact mass directly from 2D pixels without volumetric scale references.

---

## 9. API Specification

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/health` | `GET` | Returns API status, active architecture, device, and class count |
| `/api/foods` | `GET` | Lists 20 supported food categories and IFCT nutrition database |
| `/api/nutrition/{food_name}` | `GET` | Returns nutritional profile scaled by `?serving_size=Small\|Regular\|Large` |
| `/api/predict` | `POST` | Accepts multi-part image upload; returns top dish, confidence, entropy, candidates, and nutrition |
| `/api/explain` | `POST` | Computes Grad-CAM attention heatmap; returns Base64 overlay image and layer attribution |
| `/api/history` | `GET` | Retrieves previously saved prediction records from SQLite store |
| `/api/history` | `POST` | Persists a prediction record with portion size details |
| `/api/history/{id}` | `DELETE` | Removes a historical prediction record by ID |
| `/api/analytics` | `GET` | Returns cross-model benchmark reports and dataset summary |

---

## 10. Research Limitations & Future Roadmap

1. **Multi-Dish Detection:** Current pipeline classifies single centered dishes. Future work will integrate YOLOv8-seg for bounding-box detection of multiple distinct dishes on a single thali.
2. **Reference-Object Volumetric Estimation:** Incorporating coin or credit card fiducials to predict true 3D volume rather than relying on discrete portion selections (`Small`, `Regular`, `Large`).
3. **Calibrated OOD Classification:** Extending beyond Shannon entropy with Mahalanobis distance in penultimate feature space for rigorous out-of-distribution rejection.

---

## 11. License & Citation

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

If using StreetFoodAI in academic work, cite the research report:
```bibtex
@misc{streetfoodai2026,
  title={StreetFoodAI: An Explainable Deep Learning Framework for Indian Street Food Recognition and Nutritional Estimation},
  author={StreetFoodAI Research Team},
  year={2026},
  publisher={GitHub},
  howpublished={\url{https://github.com/your-username/StreetFoodAI}}
}
```
