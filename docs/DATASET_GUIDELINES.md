# StreetFoodAI: Dataset Guidelines, Curation & Provenance

## 1. Directory Structure

Datasets are structured into class-specific folders under `data/`:

```
data/
├── raw/                      # Raw uncurated images (user photos / public downloads)
│   ├── Vada Pav/
│   ├── Pav Bhaji/
│   ├── Samosa/
│   └── ... (20 categories)
├── processed/                # Curated, deduplicated, and split datasets
│   ├── train/                # 70% stratified training split
│   ├── val/                  # 15% validation split
│   └── test/                 # 15% held-out test split
└── metadata/
    └── dataset_summary.json  # Machine-readable distribution and duplicate log
```

---

## 2. Supported Public Sources & Licensing

When curating images for StreetFoodAI, only use legitimate public datasets or self-collected photographs. Document source URLs, citations, and licenses:

| Source | Reference / License | Usage Restrictions | Street Food Categories Included |
| :--- | :--- | :--- | :--- |
| **Indian Food Dataset (Kaggle)** | CC0 / Public Domain | Academic & Commercial Permitted | Vada Pav, Samosa, Dosa, Idli, Chole Bhature |
| **Food-101 (Subset)** | Bossard et al., ECCV 2014 (Open Academic) | Non-commercial research | Samosa, Omelette, Sandwich |
| **Custom Field Photos** | Project Author (CC BY 4.0) | Attribution required | Misal Pav, Bhel Puri, Sev Puri, Dabeli |

*Note: Large commercial image scrapers that violate website Terms of Service should not be used.*

---

## 3. Data Cleaning & Integrity Protocol

The automated script `scripts/prepare_data.py` executes a four-stage pipeline:

1. **Header & Structure Validation:**
   * Reads file signatures via PIL `Image.verify()`.
   * Rejects corrupt, zero-byte, or non-image files.
   * Discards images smaller than 50x50 pixels.
2. **Cryptographic Deduplication (SHA-256):**
   * Computes SHA-256 hash of image file contents.
   * Identifies identical duplicate photos and prevents split leakage (ensuring duplicate images never leak into `val/` or `test/`).
3. **Stratified Splitting:**
   * Splits images 70% Train, 15% Validation, 15% Test per class using a fixed seed (`seed=42`).
4. **Imbalance Detection:**
   * Calculates imbalance ratio: $R = \max(C) / \min(C)$.
   * Flags severe imbalance warnings when $R > 3.0$.

---

## 4. Dataset Preparation Command

To clean and split images placed in `data/raw/`:

```bash
python scripts/prepare_data.py --raw-dir data/raw --processed-dir data/processed --train-ratio 0.70 --val-ratio 0.15 --test-ratio 0.15 --seed 42
```
