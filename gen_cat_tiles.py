# -*- coding: utf-8 -*-
"""Genera la imagen de cada RUBRO a partir de una foto real de producto
representativa (img/prod/*.webp) -> img/cat/{slug}.jpg sobre fondo blanco."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.join(HERE, "img", "prod")
CAT = os.path.join(HERE, "img", "cat")
S = 520

# rubro -> tipo representativo (foto real ya descargada)
MAP = {
    "aridos": "arena",
    "cemento-cal": "cemento",
    "hierros": "hierro",
    "ladrillos": "ladrillo-hueco",
    "refractarios": "ladrillo-refra",
    "pegamentos": "pegamento",
    "aditivos": "sika",
    "alambres": "alambre",
    "pinturas": "latex",
    "pintureria": "rodillo",
    "plomeria": "cano-pvc",
    "riego": "manguera",
    "electricidad": "cable",
    "buloneria": "bulon",
    "herrajes": "bisagra",
    "herramientas": "martillo",
    "quimicos": "silicona",
    "fletes": "flete",
    "varios": "balde",
}

ok = miss = 0
for slug, key in MAP.items():
    src = os.path.join(PROD, key + ".webp")
    if not os.path.exists(src):
        print("falta", key); miss += 1; continue
    im = Image.open(src).convert("RGB")
    # lienzo blanco cuadrado, producto centrado
    canvas = Image.new("RGB", (S, S), (255, 255, 255))
    w, h = im.size
    sc = int(S * 0.92)
    im2 = im.resize((sc, sc), Image.LANCZOS)
    canvas.paste(im2, ((S - sc) // 2, (S - sc) // 2))
    canvas.save(os.path.join(CAT, slug + ".jpg"), "JPEG", quality=84)
    ok += 1
print(f"OK: {ok} | faltan: {miss}")
