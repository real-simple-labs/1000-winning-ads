#!/usr/bin/env python3
"""Combine per-brand JSON files into one dataset + report, then build the swipe file."""
import json, glob, os, re, subprocess

here = os.path.dirname(os.path.abspath(__file__))
brand_files = sorted(f for f in glob.glob(os.path.join(here, "data", "*.json"))
                     if not os.path.basename(f).startswith("missing"))
missing_files = sorted(glob.glob(os.path.join(here, "data", "missing*.json")))

brands, seen, problems = [], set(), []
total_ads = 0
for f in brand_files:
    try:
        b = json.load(open(f))
    except Exception as e:
        problems.append(f"{os.path.basename(f)}: unreadable JSON ({e})")
        continue
    name = b.get("name", "").strip()
    if not name or not b.get("ads"):
        problems.append(f"{os.path.basename(f)}: empty name or no ads")
        continue
    if name.lower() in seen:
        problems.append(f"{os.path.basename(f)}: duplicate of {name}, skipped")
        continue
    seen.add(name.lower())
    # basic ad validation
    ok_ads = []
    for ad in b["ads"]:
        if ad.get("media") and ad.get("type") in ("video", "image"):
            ad.setdefault("trend", "n/a"); ad.setdefault("angle", "")
            ad.setdefault("hook", ""); ad.setdefault("copy", "")
            ad.setdefault("title", name); ad.setdefault("days", "?")
            ad.setdefault("launch", "")
            ok_ads.append(ad)
    if not ok_ads:
        problems.append(f"{os.path.basename(f)}: no usable ads")
        continue
    b["ads"] = ok_ads
    total_ads += len(ok_ads)
    brands.append(b)

missing = []
for f in missing_files:
    try:
        m = json.load(open(f))
        for item in m.get("missing", []):
            missing.append(item.get("name", "?") + " — " + item.get("reason", ""))
    except Exception:
        pass

json.dump({"brands": brands}, open(os.path.join(here, "full-data.json"), "w"),
          ensure_ascii=False)
print(f"BRANDS: {len(brands)}  ADS: {total_ads}")
print("MISSING RECORDED:", len(missing))
for m in missing: print("  -", m)
if problems:
    print("PROBLEMS:")
    for p in problems: print("  !", p)
