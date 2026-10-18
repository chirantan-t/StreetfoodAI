# StreetFoodAI: Reproducibility Protocol & Environment Setup

## 1. Reproducibility Guarantees

* **Fixed Random Seed:** Default random seed `42` is enforced across NumPy, PyTorch, and Python `random` for data splitting, weight initialization, and data augmentation.
* **Deterministic Stratification:** Training, validation, and test splits are deterministically stratified by food category.
* **Hardware Profiling:** Hardware specifications (CPU/GPU processor, PyTorch build, thread pool) are systematically recorded with latency benchmarks.

---

## 2. Local Environment Reproduction

```bash
# 1. Clone repository and navigate
cd StreetFoodAI

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Verify test suite (18 unit/integration tests)
python -m pytest -v

# 4. Profile model latencies and parameter counts
python ml/evaluation/compare.py

# 5. Start Backend API Server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# 6. In a second terminal, start Frontend Vite Dev Server
cd frontend
npm install
npm run dev
```

---

## 3. Google Colab GPU Reproduction

A dedicated self-contained notebook is available at `notebooks/02_colab_training_pipeline.ipynb`.

### Execution Steps in Colab:
1. Open Google Colab and set Runtime to **GPU (T4 or A100)**.
2. Clone the repository:
   ```bash
   !git clone https://github.com/your-repo/StreetFoodAI.git
   %cd StreetFoodAI
   !pip install -r backend/requirements.txt
   ```
3. Prepare the dataset:
   ```bash
   !python scripts/prepare_data.py --raw-dir data/raw --processed-dir data/processed
   ```
4. Run full fine-tuning on GPU:
   ```bash
   !python scripts/train_model.py --model mobilenet_v3_large --epochs 30 --batch-size 32 --lr 1e-4
   ```
5. Export checkpoints and ONNX bundle:
   ```bash
   !python scripts/export_onnx.py --model mobilenet_v3_large --weights ml/checkpoints/best_mobilenet_v3_large.pth
   ```
