#!/usr/bin/env python3
"""
Enrich StreetFoodAI raw dataset by fetching verified images across all 20 classes
from Wikimedia Commons with proper rate-limiting and standard thumbnail URLs.
"""
import time
import hashlib
import re
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "StreetFoodAI-DatasetCollector/2.0 (educational research; contact@streetfoodai.local)"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

RAW_DIR = Path("data/raw")

CATEGORIES = {
    "Vada Pav": ["vada pav Mumbai", "batata vada pav", "vada pav plate", "vada pao snack"],
    "Pav Bhaji": ["pav bhaji plate", "Mumbai pav bhaji", "pav bhaji butter", "pav bhaji tawa"],
    "Misal Pav": ["misal pav plate", "puneri misal pav", "kolhapuri misal", "misal pav farsan"],
    "Pani Puri": ["pani puri golgappa", "golgappa plate", "panipuri Indian street food", "puchka chaat"],
    "Bhel Puri": ["bhel puri chaat", "bhelpuri Mumbai", "bhel puri sev", "Indian bhelpuri"],
    "Sev Puri": ["sev puri chaat", "sev batata puri", "sev puri Mumbai", "sev puri plate"],
    "Dabeli": ["kutchi dabeli", "dabeli pav", "dabeli street food", "dabeli snack"],
    "Samosa": ["samosa plate", "potato samosa Indian", "samosa chutney", "crispy samosa"],
    "Kachori": ["khasta kachori", "pyaaz kachori", "raj kachori", "kachori Indian snack"],
    "Dosa": ["masala dosa plate", "crispy dosa sambar", "South Indian dosa", "plain dosa chutney"],
    "Idli": ["idli sambar plate", "steamed idli chutney", "idli vada South Indian", "idli plate"],
    "Medu Vada": ["medu vada plate", "vada sambar South Indian", "crispy medu vada", "urad dal vada"],
    "Poha": ["kanda poha plate", "indori poha", "poha breakfast Indian", "flattened rice poha"],
    "Upma": ["rava upma plate", "sooji upma breakfast", "semolina upma", "South Indian upma"],
    "Chole Bhature": ["chole bhature plate", "chana bhatura Punjabi", "amritsari chole bhature", "chole bhature"],
    "Aloo Tikki": ["aloo tikki chaat", "crispy aloo tikki", "aloo tikki plate", "potato tikki"],
    "Frankie": ["kathi roll", "veg frankie roll", "paneer roll wrap", "frankie roll"],
    "Sandwich": ["bombay vegetable sandwich", "mumbai veg sandwich", "grilled vegetable sandwich", "toast sandwich"],
    "Jalebi": ["jalebi Indian sweet", "crispy jalebi", "hot jalebi plate", "jalebi"],
    "Other _ Unknown Food": ["empty dining table", "kitchen utensils bowl", "empty plate background", "restaurant table"]
}

def commons_search(query, limit=20):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrnamespace": 6,
        "gsrlimit": min(limit, 30),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": 800
    }
    try:
        r = SESSION.get(API, params=params, timeout=25)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            return list(pages.values())
    except Exception as e:
        print(f"  [Search Error] {query}: {e}")
    return []

def enrich():
    print("=== Starting StreetFoodAI Dataset Enrichment ===")
    seen_hashes = set()

    # Preload existing hashes to avoid duplicates
    for f in RAW_DIR.rglob("*"):
        if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            try:
                seen_hashes.add(hashlib.sha256(f.read_bytes()).hexdigest())
            except Exception:
                pass

    print(f"Preloaded {len(seen_hashes)} existing images in data/raw.")

    for class_name, queries in CATEGORIES.items():
        folder = RAW_DIR / class_name
        folder.mkdir(parents=True, exist_ok=True)
        current_images = [img for img in folder.glob("*") if img.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]]
        count = len(current_images)
        target = 25 # Target at least 25 per class

        print(f"\n--> {class_name}: currently {count} images (target: {target})")
        if count >= target:
            continue

        for q in queries:
            if count >= target:
                break
            pages = commons_search(q, limit=25)
            time.sleep(0.5)

            for page in pages:
                if count >= target:
                    break
                infos = page.get("imageinfo") or []
                if not infos:
                    continue
                info = infos[0]
                url = info.get("thumburl") or info.get("url")
                if not url or info.get("mime") not in ("image/jpeg", "image/png", "image/webp"):
                    continue

                try:
                    res = SESSION.get(url, timeout=30)
                    if res.status_code == 429:
                        print("  [Rate limited 429] Backing off 3s...")
                        time.sleep(3.0)
                        continue
                    if res.status_code != 200:
                        continue

                    raw = res.content
                    digest = hashlib.sha256(raw).hexdigest()
                    if digest in seen_hashes:
                        continue

                    img = Image.open(BytesIO(raw)).convert("RGB")
                    if img.width < 150 or img.height < 150:
                        continue

                    seen_hashes.add(digest)
                    filename = f"{re.sub(r'[^a-z0-9]+', '_', class_name.lower())}_{count+1:03d}.jpg"
                    dest = folder / filename
                    img.save(dest, "JPEG", quality=90, optimize=True)
                    count += 1
                    print(f"  + Added: {filename} ({img.size[0]}x{img.size[1]})")
                    time.sleep(0.4)
                except Exception as e:
                    continue

        print(f"  Finished {class_name}: now has {count} images.")

    print("\nEnrichment complete! All categories populated.")

if __name__ == "__main__":
    enrich()
