# -*- coding: utf-8 -*-
"""Descarga las imágenes reales recolectadas (img_urls.txt), las recorta
cuadradas y las optimiza a WebP 400x400 en img/prod/{key}.webp."""
import os, io, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img", "prod")
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
SIZE = 400

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def square(im):
    im = im.convert("RGB")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    return im.resize((SIZE, SIZE), Image.LANCZOS)

rows = []
for line in open(os.path.join(HERE, "img_urls.txt"), encoding="utf-8"):
    line = line.strip()
    if not line or "|" not in line:
        continue
    k, u = line.split("|", 1)
    rows.append((k.strip(), u.strip()))

ok = fail = 0
seen = set()
for key, url in rows:
    if key in seen:
        continue
    seen.add(key)
    try:
        raw = fetch(url)
        if len(raw) < 2000:
            raise ValueError("muy chica")
        im = Image.open(io.BytesIO(raw))
        square(im).save(os.path.join(OUT, key + ".webp"), "WEBP", quality=78, method=4)
        ok += 1
    except Exception as e:
        fail += 1
        print("FAIL", key, str(e)[:50])
print(f"\nOK: {ok} | fail: {fail} | tipos: {len(seen)}")
