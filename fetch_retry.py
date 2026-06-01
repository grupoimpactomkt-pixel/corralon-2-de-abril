# -*- coding: utf-8 -*-
"""Reintenta los tipos sin imagen con varias queries alternativas."""
import os, io, concurrent.futures
from PIL import Image
import fetch_type_images as F

ALT = {
 "bolson-arido": ["bulk ton bag sand FIBC", "big bag aggregate construction", "jumbo bag sand"],
 "piedra": ["gravel pile stones", "crushed stone aggregate", "pile of gravel"],
 "cal": ["bag of lime powder", "hydrated lime sack", "lime powder cement"],
 "yeso": ["bag of plaster powder", "gypsum plaster sack", "plaster of paris bag"],
 "hidralit": ["bag of lime", "lime mortar bag", "hydrated lime"],
 "malla": ["welded wire mesh panel", "reinforcement steel mesh", "wire mesh fence panel"],
 "ladrillo-telgopor": ["styrofoam block", "eps foam insulation block", "polystyrene block"],
 "tejuela-refra": ["clay brick tile", "terracotta tile", "thin brick tile"],
 "masilla-durlock": ["joint compound bucket", "drywall spackle bucket", "wall filler bucket"],
 "fino": ["bag of plaster", "fine cement bag", "render plaster bag"],
 "mortero-mix": ["bag of mortar mix", "concrete mix bag", "cement mortar sack"],
 "pegamento": ["tile adhesive bucket", "thinset mortar bag", "ceramic tile glue"],
 "sika": ["construction adhesive bottle", "sealant bottle", "bonding agent bottle"],
 "membrana-rollo": ["bitumen roofing roll", "roofing felt roll", "waterproof membrane roll"],
 "membrana": ["roof coating bucket", "waterproofing paint bucket", "liquid rubber bucket"],
 "latex": ["wall paint bucket", "paint can white", "interior paint bucket"],
 "antioxido": ["metal primer paint can", "rust converter can", "red oxide primer"],
 "enduido": ["spackling paste bucket", "wall putty bucket", "skim coat bucket"],
 "fijador": ["paint primer can", "sealer primer bucket", "wall primer"],
 "masilla": ["wood filler putty", "putty knife filler", "filler paste tube"],
 "cano-estruct-p": ["ppr green pipe", "plastic plumbing pipe", "polypropylene pipe"],
 "codo-pvc": ["pvc pipe elbow fitting", "plumbing elbow", "pipe elbow 90"],
 "ramal-pvc": ["pvc pipe tee fitting", "plumbing tee fitting", "pipe wye fitting"],
 "sifon": ["sink p-trap", "plumbing trap pipe", "drain trap"],
 "flexible": ["braided flexible hose", "flexible water connector", "flexible tap hose"],
 "teflon": ["ptfe thread tape roll", "plumbers tape", "thread seal tape"],
 "tapa-pvc": ["pvc pipe end cap", "pipe cap fitting", "plug cap pipe"],
 "mariposa": ["wing nut", "butterfly nut bolt", "thumb nut"],
 "tarugo": ["wall plug anchor", "plastic dowel anchor", "expansion anchor"],
 "tenaza": ["carpenter pincers", "pincer pliers tool", "nipper pliers"],
 "sellador": ["sealant cartridge tube", "caulk tube", "polyurethane sealant"],
 "espuma-pu": ["spray foam can", "expanding foam canister", "polyurethane foam spray"],
}

def work(item):
    key, queries = item
    dest = os.path.join(F.OUT, key + ".webp")
    if os.path.exists(dest):
        return (key, "have")
    for q in queries:
        try:
            for u in F.ov_urls(q, 10):
                try:
                    raw = F.fetch(u)
                    if len(raw) < 6000:
                        continue
                    im = Image.open(io.BytesIO(raw))
                    if min(im.size) < 160:
                        continue
                    F.square(im).save(dest, "WEBP", quality=72, method=4)
                    return (key, "ok:" + q)
                except Exception:
                    continue
        except Exception:
            continue
    return (key, "FAIL")

okc = failc = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for key, st in ex.map(work, ALT.items()):
        if st.startswith("ok"): okc += 1
        elif st == "FAIL": failc += 1; print("  FAIL", key)
        if st.startswith("ok"): print("  OK  ", key)
print(f"\nrecuperados: {okc} | siguen sin imagen: {failc}")
