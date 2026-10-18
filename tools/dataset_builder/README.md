# StreetFoodAI — Real-Photo Dataset Builder

This package builds a **real-photograph dataset** for the 20 StreetFoodAI classes and can compute image embeddings locally.

## Important
This ZIP is a **dataset builder**, not a ZIP of downloaded photographs. The current chat runtime cannot reliably download external image files into the archive. Run the included downloader on a computer/Antigravity environment with internet access to fetch the images.

The script searches Wikimedia Commons and downloads available image files, recording source pages, authors, license information, and direct source URLs where exposed by Commons metadata. Search results are not guaranteed to be perfectly labelled, so review `metadata/images.csv` before training.

## Recommended starter size
- Target: **10 accepted photos per class** (up to 200 images).
- Wikimedia may not have 10 suitable photos for every niche category. The script reports shortages instead of inventing images.
- Treat this as a starter/reference dataset. For a reliable classifier, aim for hundreds of varied, correctly labelled photos per class and add your own photos.
- Do not split near-duplicate or same-source images across train/test. Review the dataset and licensing before publishing it.

## Quick start

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python scripts/download_commons_dataset.py --per-class 10
```

Downloaded images are stored as:

```text
data/
  images/
    00_vada_pav/
    ...
    19_other_unknown_food/
  metadata/
    images.csv
    download_report.json
```

### Generate image embeddings (optional)

```bash
pip install -r requirements-embeddings.txt
python scripts/generate_embeddings.py
```

This uses OpenCLIP's pretrained ViT-B-32 model and writes:
- `data/embeddings/embeddings.npy`
- `data/embeddings/embedding_index.csv`

Embeddings are model-specific numerical representations, not calorie labels. Keep the model name and preprocessing consistent when comparing a new upload against stored embeddings. The first run may download pretrained weights.

## Unknown / out-of-distribution class
`Other / Unknown Food` is intentionally populated from non-food object searches. It is not a substitute for a principled out-of-distribution detector. Review these images and evaluate rejection thresholds using held-out classes and non-food images.

## License and attribution
Images retain the licenses and attribution of their original authors. Check `metadata/images.csv` and each source page before reuse. This tool does not guarantee that every search result is suitable; remove unrelated or incorrectly labelled images manually. Follow each image's specific license terms.
