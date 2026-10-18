#!/usr/bin/env python3
"""Download real food photographs from Wikimedia Commons with attribution metadata."""
import argparse, csv, json, re, time, hashlib, sys
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "classes.json"
OUT = ROOT / "data" / "images"
META = ROOT / "data" / "metadata"
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "StreetFoodAI-DatasetBuilder/1.0 (educational project; contact repository maintainer)"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def safe_name(s):
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("._")
    return s[:100] or "image"

def commons_search(query, limit=40):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": "filetype:bitmap " + query, "gsrnamespace": 6,
        "gsrlimit": min(limit, 50),
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1200
    }
    try:
        r = SESSION.get(API, params=params, timeout=35)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        return list(pages.values())
    except Exception as e:
        print(f"  Search error for {query!r}: {e}")
        return []

def get_meta(page):
    infos = page.get("imageinfo") or []
    if not infos:
        return None
    ii = infos[0]
    ext = ii.get("extmetadata", {})
    def val(key):
        raw = ext.get(key, {}).get("value", "")
        return re.sub("<[^>]+>", "", str(raw)).strip()
    return {
        "title": page.get("title", ""),
        "page_url": ii.get("descriptionurl", ""),
        "file_url": ii.get("thumburl") or ii.get("url", ""),
        "original_url": ii.get("url", ""),
        "mime": ii.get("mime", ""),
        "width": ii.get("width", 0),
        "height": ii.get("height", 0),
        "artist": val("Artist"),
        "credit": val("Credit"),
        "license_short_name": val("LicenseShortName"),
        "license_url": val("LicenseUrl"),
        "usage_terms": val("UsageTerms"),
        "attribution_required": val("AttributionRequired"),
        "image_description": val("ImageDescription"),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=10, help="Target number of accepted photos per class (default: 10)")
    ap.add_argument("--min-width", type=int, default=256)
    ap.add_argument("--min-height", type=int, default=256)
    ap.add_argument("--delay", type=float, default=0.35, help="Delay between requests")
    args = ap.parse_args()
    if args.per_class < 1:
        ap.error("--per-class must be >= 1")
    classes = json.loads(CONFIG.read_text(encoding="utf-8"))
    META.mkdir(parents=True, exist_ok=True)
    rows, report = [], []
    seen_hashes = set()
    for cls in classes:
        folder = OUT / cls["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        existing = list(folder.glob("*.jpg")) + list(folder.glob("*.png")) + list(folder.glob("*.webp"))
        count = len(existing)
        print(f"\n[{cls['class_index']:02d}] {cls['class_name']}: target {args.per_class}; existing {count}")
        tried_titles = set()
        for query in cls["search_queries"]:
            if count >= args.per_class:
                break
            pages = commons_search(query, limit=50)
            time.sleep(args.delay)
            for page in pages:
                if count >= args.per_class:
                    break
                title = page.get("title", "")
                if title in tried_titles:
                    continue
                tried_titles.add(title)
                info = get_meta(page)
                if not info or not info["file_url"]:
                    continue
                if info["mime"] not in ("image/jpeg", "image/png", "image/webp"):
                    continue
                if int(info["width"] or 0) < args.min_width or int(info["height"] or 0) < args.min_height:
                    continue
                try:
                    response = SESSION.get(info["file_url"], timeout=45)
                    response.raise_for_status()
                    raw = response.content
                    digest = hashlib.sha256(raw).hexdigest()
                    if digest in seen_hashes:
                        continue
                    im = Image.open(BytesIO(raw))
                    im.verify()
                    im = Image.open(BytesIO(raw)).convert("RGB")
                    if im.width < args.min_width or im.height < args.min_height:
                        continue
                    seen_hashes.add(digest)
                    filename = f"{cls['class_index']:02d}_{safe_name(cls['class_name'].lower().replace(' ', '_'))}_{count+1:03d}.jpg"
                    dest = folder / filename
                    Image.open(BytesIO(raw)).convert("RGB").save(dest, "JPEG", quality=92, optimize=True)
                    info.update({
                        "image_id": f"{cls['class_index']:02d}_{count+1:03d}",
                        "class_index": cls["class_index"],
                        "class_name": cls["class_name"],
                        "folder": cls["folder"],
                        "filename": filename,
                        "local_path": str(dest.relative_to(ROOT)).replace("\\", "/"),
                        "sha256": digest,
                        "query_used": query,
                        "download_status": "downloaded"
                    })
                    rows.append(info)
                    count += 1
                    print(f"  + {filename} [{info['license_short_name'] or 'license metadata missing'}]")
                    time.sleep(args.delay)
                except (requests.RequestException, UnidentifiedImageError, OSError) as e:
                    print(f"  - skipped {title}: {e}")
                    continue
        report.append({
            "class_index": cls["class_index"], "class_name": cls["class_name"],
            "target": args.per_class, "downloaded_this_run_or_existing": count,
            "shortfall": max(0, args.per_class-count)
        })
        if count < args.per_class:
            print(f"  WARNING: only {count} accepted images; short by {args.per_class-count}.")
    csv_path = META / "images.csv"
    fieldnames = sorted({k for row in rows for k in row.keys()}) if rows else [
        "image_id","class_index","class_name","filename","page_url","file_url","artist","license_short_name","license_url"
    ]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    (META / "download_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nFinished.")
    print(f"Metadata: {csv_path}")
    print(f"Report: {META / 'download_report.json'}")
    print("Review every image and its license/attribution before training or redistributing.")
    if any(r["shortfall"] for r in report):
        print("Some classes have fewer than the requested images. Add your own photos or use a properly licensed dataset.")
if __name__ == "__main__":
    main()
