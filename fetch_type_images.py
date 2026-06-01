# -*- coding: utf-8 -*-
"""Descarga 1 imagen representativa real por TIPO de producto (Openverse, CC),
la recorta cuadrada y la guarda optimizada en img/prod/{key}.webp (~400px).
Uso:
    python fetch_type_images.py            # solo los que faltan
    python fetch_type_images.py --force    # vuelve a bajar todos
"""
import os, io, sys, json, time, urllib.request, urllib.parse, concurrent.futures
from PIL import Image
from types_def import TYPES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img", "prod")
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (corralon-catalog/1.0)"
SIZE = 400
FORCE = "--force" in sys.argv

def ov_urls(q, n=8):
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({
        "q": q, "page_size": n, "license_type": "commercial",
        "mature": "false", "aspect_ratio": "square,wide",
    })
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return [x["url"] for x in d.get("results", []) if x.get("url")]

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def square(im):
    im = im.convert("RGB")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    return im.resize((SIZE, SIZE), Image.LANCZOS)

def do_type(t):
    key, cat, query, kws = t
    dest = os.path.join(OUT, key + ".webp")
    if os.path.exists(dest) and not FORCE:
        return (key, "skip")
    try:
        for u in ov_urls(query):
            try:
                raw = fetch(u)
                if len(raw) < 7000:
                    continue
                im = Image.open(io.BytesIO(raw))
                if min(im.size) < 180:
                    continue
                square(im).save(dest, "WEBP", quality=72, method=4)
                return (key, "ok")
            except Exception:
                continue
    except Exception as e:
        return (key, "qerr:" + str(e)[:40])
    return (key, "FAIL")

def main():
    todo = TYPES
    print(f"Tipos: {len(todo)} | destino: {OUT}")
    ok = fail = skip = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for key, status in ex.map(do_type, todo):
            if status == "ok": ok += 1
            elif status == "skip": skip += 1
            else: fail += 1; print(f"  [{status}] {key}")
    print(f"\nOK: {ok} | skip: {skip} | fail: {fail}")

if __name__ == "__main__":
    main()
