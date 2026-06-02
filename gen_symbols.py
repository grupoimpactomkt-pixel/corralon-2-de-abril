# -*- coding: utf-8 -*-
"""Genera símbolos SVG patrios: Sol de Mayo y silueta de Malvinas."""
import math, os
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
os.makedirs(A, exist_ok=True)

GOLD = "#F4B824"
GOLD_DK = "#E09A0B"

def sol(size=200, rays=32, face=True, color=GOLD, dark=GOLD_DK):
    cx = cy = size / 2
    rc = size * 0.20          # radio del disco central
    r1 = size * 0.30          # base de los rayos
    rlong = size * 0.48       # punta rayo largo
    rshort = size * 0.40      # punta rayo corto
    half = (math.pi / rays)   # medio ancho angular de cada rayo
    paths = []
    for i in range(rays):
        a = (2 * math.pi * i / rays) - math.pi / 2
        tip = rlong if i % 2 == 0 else rshort
        bw = half * 0.62
        x1 = cx + r1 * math.cos(a - bw); y1 = cy + r1 * math.sin(a - bw)
        x2 = cx + tip * math.cos(a);     y2 = cy + tip * math.sin(a)
        x3 = cx + r1 * math.cos(a + bw); y3 = cy + r1 * math.sin(a + bw)
        paths.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f} L{x3:.1f},{y3:.1f} Z"/>')
    rays_svg = "\n    ".join(paths)
    face_svg = ""
    if face:
        ex = rc * 0.42; ey = rc * 0.18; er = rc * 0.10
        face_svg = f'''
    <g fill="{dark}" opacity="0.85">
      <circle cx="{cx-ex:.1f}" cy="{cy-ey:.1f}" r="{er:.1f}"/>
      <circle cx="{cx+ex:.1f}" cy="{cy-ey:.1f}" r="{er:.1f}"/>
      <path d="M{cx-ex:.1f},{cy+rc*0.30:.1f} Q{cx:.1f},{cy+rc*0.62:.1f} {cx+ex:.1f},{cy+rc*0.30:.1f}"
            fill="none" stroke="{dark}" stroke-width="{rc*0.13:.1f}" stroke-linecap="round"/>
      <path d="M{cx-ex*1.15:.1f},{cy-ey*2.1:.1f} Q{cx-ex:.1f},{cy-ey*2.7:.1f} {cx-ex*0.55:.1f},{cy-ey*2.1:.1f}"
            fill="none" stroke="{dark}" stroke-width="{rc*0.10:.1f}" stroke-linecap="round"/>
      <path d="M{cx+ex*0.55:.1f},{cy-ey*2.1:.1f} Q{cx+ex:.1f},{cy-ey*2.7:.1f} {cx+ex*1.15:.1f},{cy-ey*2.1:.1f}"
            fill="none" stroke="{dark}" stroke-width="{rc*0.10:.1f}" stroke-linecap="round"/>
    </g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <g fill="{color}">
    {rays_svg}
  </g>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rc:.1f}" fill="{color}"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rc:.1f}" fill="none" stroke="{dark}" stroke-width="{size*0.012:.1f}"/>{face_svg}
</svg>
'''

# Silueta estilizada de las Islas Malvinas (Gran Malvina + Soledad con istmo)
def malvinas(w=240, h=150, fill="#FFFFFF", stroke="#0C2D52"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <g fill="{fill}" stroke="{stroke}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
    <!-- Gran Malvina (oeste): más vertical y angosta -->
    <path d="M58,26 C74,24 84,36 82,50 C80,62 90,68 86,80 C83,92 90,100 82,110
             C76,118 62,116 58,106 C54,98 60,90 50,84 C40,78 40,62 48,54
             C42,46 46,32 58,26 Z"/>
    <!-- Isla Soledad (este): más grande, con istmo y lóbulo sur (Lafonia) -->
    <path d="M150,24 C184,20 210,34 208,54 C206,70 190,72 198,84 C205,94 196,104 182,102
             C170,100 172,90 160,90 C152,96 152,110 162,118 C152,128 132,124 130,112
             C128,100 140,96 134,86 C122,82 116,52 132,38 C137,30 143,26 150,24 Z"/>
  </g>
</svg>
'''

CELESTE = "#6CACE4"
CELESTE_DK = "#3A78B8"
NAVY = "#0C2D52"

def sun_rays(cx, cy, rays, r1, rlong, rshort, color):
    out = []
    for i in range(rays):
        a = (2 * math.pi * i / rays) - math.pi / 2
        tip = rlong if i % 2 == 0 else rshort
        bw = (math.pi / rays) * 0.6
        x1 = cx + r1 * math.cos(a - bw); y1 = cy + r1 * math.sin(a - bw)
        x2 = cx + tip * math.cos(a);     y2 = cy + tip * math.sin(a)
        x3 = cx + r1 * math.cos(a + bw); y3 = cy + r1 * math.sin(a + bw)
        out.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f} L{x3:.1f},{y3:.1f} Z" fill="{color}"/>')
    return "\n      ".join(out)

def emblem(size=120):
    cx, cy = size/2, size*0.46
    rays = sun_rays(cx, cy, 24, size*0.18, size*0.40, size*0.33, GOLD)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <linearGradient id="cel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{CELESTE}"/><stop offset="1" stop-color="{CELESTE_DK}"/>
    </linearGradient>
    <clipPath id="rc"><rect x="3" y="3" width="{size-6}" height="{size-6}" rx="26"/></clipPath>
  </defs>
  <g clip-path="url(#rc)">
    <rect x="3" y="3" width="{size-6}" height="{size-6}" fill="url(#cel)"/>
    <!-- Sol de Mayo -->
    <g>{rays}</g>
    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{size*0.155:.1f}" fill="{GOLD}" stroke="{GOLD_DK}" stroke-width="1.6"/>
    <g fill="{GOLD_DK}" opacity="0.85">
      <circle cx="{cx-size*0.06:.1f}" cy="{cy-size*0.02:.1f}" r="{size*0.018:.1f}"/>
      <circle cx="{cx+size*0.06:.1f}" cy="{cy-size*0.02:.1f}" r="{size*0.018:.1f}"/>
      <path d="M{cx-size*0.055:.1f},{cy+size*0.05:.1f} Q{cx:.1f},{cy+size*0.10:.1f} {cx+size*0.055:.1f},{cy+size*0.05:.1f}"
            fill="none" stroke="{GOLD_DK}" stroke-width="2.4" stroke-linecap="round"/>
    </g>
    <!-- techo / construcción (blanco) -->
    <path d="M{size*0.16:.1f},{size*0.82:.1f} L{size*0.5:.1f},{size*0.6:.1f} L{size*0.84:.1f},{size*0.82:.1f} Z" fill="#fff"/>
    <rect x="{size*0.24:.1f}" y="{size*0.8:.1f}" width="{size*0.52:.1f}" height="{size*0.16:.1f}" fill="#fff"/>
    <rect x="{size*0.3:.1f}" y="{size*0.84:.1f}" width="{size*0.16:.1f}" height="{size*0.12:.1f}" fill="{CELESTE}"/>
    <rect x="{size*0.54:.1f}" y="{size*0.84:.1f}" width="{size*0.16:.1f}" height="{size*0.12:.1f}" fill="{CELESTE}"/>
  </g>
</svg>
'''

def logo(w=380, h=104):
    em = emblem(88).split(">", 1)[1].rsplit("</svg>", 1)[0]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <g transform="translate(6,8)">{em}</g>
  <g transform="translate(108,0)" font-family="Inter, Arial, sans-serif">
    <text x="0" y="38" font-size="18" font-weight="700" letter-spacing="5" fill="{CELESTE_DK}">CORRALÓN</text>
    <text x="0" y="70" font-size="34" font-weight="900" fill="{NAVY}">2 DE ABRIL</text>
    <text x="2" y="90" font-size="11" font-weight="600" letter-spacing="1.4" fill="#5a6b7d">MATERIALES PARA LA CONSTRUCCIÓN</text>
  </g>
</svg>
'''

def malvinas_paths(cx, cy, scale, fill="#fff", stroke="#0C2D52", sw=2.4):
    # versión compacta centrada en (cx,cy) escalada
    def tp(pts):
        return " ".join(pts)
    # reusa la silueta (coordenadas base ~ viewBox 240x150, centro ~120,75)
    import re
    raw = malvinas()
    paths = re.findall(r'<path d="([^"]+)"', raw)
    out = []
    for d in paths:
        # transformar cada número: (n-120)*scale+cx para x, (n-75)*scale+cy para y
        nums = re.findall(r'-?\d+\.?\d*', d)
        toks = re.split(r'(-?\d+\.?\d*)', d)
        idx = 0; res = []; coord = 0
        for t in toks:
            if re.fullmatch(r'-?\d+\.?\d*', t or ''):
                v = float(t)
                if coord % 2 == 0:
                    v = (v - 120) * scale + cx
                else:
                    v = (v - 75) * scale + cy
                res.append(f'{v:.1f}'); coord += 1
            else:
                res.append(t)
        out.append('<path d="' + ''.join(res) + f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')
    return "\n    ".join(out)

def badge(size=200):
    cx = cy = size/2
    rt = size*0.395
    rr = size*0.475
    malv = malvinas_paths(cx, cy*0.96, size*0.0022, fill="#fff", stroke=NAVY, sw=size*0.012)
    top = f"M{cx-rt:.1f},{cy:.1f} A{rt:.1f},{rt:.1f} 0 0 1 {cx+rt:.1f},{cy:.1f}"
    bot = f"M{cx+rt*0.99:.1f},{cy*1.02:.1f} A{rt:.1f},{rt:.1f} 0 0 1 {cx-rt*0.99:.1f},{cy*1.02:.1f}"
    fs = size*0.082
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <radialGradient id="bg" cx="0.5" cy="0.4" r="0.7">
      <stop offset="0" stop-color="#8fc1ea"/><stop offset="0.6" stop-color="{CELESTE}"/>
      <stop offset="1" stop-color="{CELESTE_DK}"/>
    </radialGradient>
    <path id="ptop" d="{top}"/>
    <path id="pbot" d="{bot}"/>
  </defs>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="url(#bg)" stroke="{GOLD}" stroke-width="{size*0.03:.1f}"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr-size*0.045:.1f}" fill="none" stroke="#fff" stroke-width="{size*0.006:.1f}" opacity="0.6"/>
  <g>
    {malv}
  </g>
  <text font-family="Inter, Arial, sans-serif" font-weight="800" font-size="{fs:.1f}" fill="{NAVY}" letter-spacing="1">
    <textPath href="#ptop" startOffset="50%" text-anchor="middle">CORRALÓN 2 DE ABRIL</textPath>
  </text>
  <text font-family="Inter, Arial, sans-serif" font-weight="700" font-size="{fs*0.86:.1f}" fill="#fff" letter-spacing="1.5">
    <textPath href="#pbot" startOffset="50%" text-anchor="middle">POR SIEMPRE ARGENTINAS</textPath>
  </text>
</svg>
'''

def logo2(w=400, h=104):
    em = badge(92).split(">", 1)[1].rsplit("</svg>", 1)[0]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <g transform="translate(4,6)">{em}</g>
  <g transform="translate(112,0)" font-family="Inter, Arial, sans-serif">
    <text x="0" y="40" font-size="19" font-weight="700" letter-spacing="4" fill="{CELESTE_DK}">CORRALÓN</text>
    <text x="0" y="72" font-size="35" font-weight="900" fill="{NAVY}">2 DE ABRIL</text>
    <text x="2" y="91" font-size="10.5" font-weight="600" letter-spacing="1.2" fill="#5a6b7d">CORRALÓN Y FERRETERÍA · MAR DEL PLATA</text>
  </g>
</svg>
'''

open(os.path.join(A, "sol.svg"), "w", encoding="utf-8").write(sol())
open(os.path.join(A, "malvinas.svg"), "w", encoding="utf-8").write(malvinas())
open(os.path.join(A, "emblem.svg"), "w", encoding="utf-8").write(badge(120))
open(os.path.join(A, "logo.svg"), "w", encoding="utf-8").write(logo2())
print("OK: sol.svg, malvinas.svg, emblem.svg(badge), logo.svg")
