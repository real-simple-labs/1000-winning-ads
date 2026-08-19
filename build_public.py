#!/usr/bin/env python3
"""Build a fully self-contained public swipe file: every image baked in as a data URI.
Statics -> resized WebP. Videos -> first frame via ffmpeg + click-through to watch."""
import json, os, io, base64, subprocess, hashlib, sys
from concurrent.futures import ThreadPoolExecutor
import urllib.request
from PIL import Image
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".media-cache")
os.makedirs(CACHE, exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

AD_W, AD_Q = 264, 62          # ad thumbnails
LOGO_W, LOGO_Q = 56, 70       # brand logos
TARGET_KB = 8                # per-ad ceiling before extra compression

def cache_path(url, kind):
    return os.path.join(CACHE, hashlib.md5((kind + url).encode()).hexdigest() + ".webp")

def encode(img, width, quality, target_kb=None):
    img = img.convert("RGB")
    if img.width > width:
        img = img.resize((width, max(1, int(img.height * width / img.width))), Image.LANCZOS)
    for q in [quality, 55, 45, 35]:
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=q, method=4)
        data = buf.getvalue()
        if target_kb is None or len(data) <= target_kb * 1024:
            return data
    return data

def fetch_bytes(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def get_image(url, width, quality, target_kb=None):
    """Download a still image -> compressed webp bytes."""
    cp = cache_path(url, f"img{width}")
    if os.path.exists(cp):
        return open(cp, "rb").read()
    data = fetch_bytes(url)
    out = encode(Image.open(io.BytesIO(data)), width, quality, target_kb)
    open(cp, "wb").write(out)
    return out

def get_video_frame(url, width, quality, target_kb=None):
    """Pull the first frame straight from the remote video (no full download)."""
    cp = cache_path(url, f"vid{width}")
    if os.path.exists(cp):
        return open(cp, "rb").read()
    tmp = cp + ".jpg"
    r = subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", url, "-vframes", "1",
         "-vf", f"scale={width*2}:-1", "-q:v", "6", tmp],
        capture_output=True, timeout=120)
    if r.returncode != 0 or not os.path.exists(tmp):
        raise RuntimeError("ffmpeg failed")
    out = encode(Image.open(tmp), width, quality, target_kb)
    os.remove(tmp)
    open(cp, "wb").write(out)
    return out

def as_uri(b):
    return "data:image/webp;base64," + base64.b64encode(b).decode()

data = json.load(open(os.path.join(HERE, "full-data.json")))
brands = data["brands"]

jobs = []
for bi, b in enumerate(brands):
    if b.get("logo"):
        jobs.append(("logo", bi, None, b["logo"]))
    for ai, ad in enumerate(b["ads"]):
        jobs.append((ad["type"], bi, ai, ad["media"]))

print(f"fetching {len(jobs)} assets...", flush=True)
results, failures = {}, []

def work(job):
    kind, bi, ai, url = job
    try:
        if kind == "logo":
            return job, get_image(url, LOGO_W, LOGO_Q, 3)
        if kind == "video":
            return job, get_video_frame(url, AD_W, AD_Q, TARGET_KB)
        return job, get_image(url, AD_W, AD_Q, TARGET_KB)
    except Exception as e:
        return job, None

with ThreadPoolExecutor(max_workers=14) as ex:
    for n, (job, out) in enumerate(ex.map(work, jobs), 1):
        if out is None:
            failures.append(job)
        else:
            results[(job[0], job[1], job[2])] = out
        if n % 100 == 0:
            print(f"  {n}/{len(jobs)}", flush=True)

total = sum(len(v) for v in results.values())
print(f"done. ok={len(results)} failed={len(failures)} binary={total/1048576:.1f}MB "
      f"(~{total*1.34/1048576:.1f}MB base64)", flush=True)
json.dump({"ok": len(results), "failed": len(failures),
           "failures": [[j[0], brands[j[1]]['name'], j[2]] for j in failures]},
          open(os.path.join(HERE, "embed-report.json"), "w"), indent=1)
