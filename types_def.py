# -*- coding: utf-8 -*-
"""
Tipos de producto para imágenes representativas reales.
Cada tipo: (key, cat, query_en, [keywords]).
- key   : nombre de archivo -> img/prod/{key}.webp
- cat   : categoría a la que pertenece (el match solo se prueba dentro de esa cat)
- query : términos en inglés para buscar la foto (Openverse / CC)
- keywords: si alguno aparece en el nombre del producto, se asigna este tipo
El ORDEN importa dentro de cada categoría (gana el primero). Lo no asignado usa
la imagen de la categoría como respaldo.
"""

TYPES = [
    # ---------------- ÁRIDOS ----------------
    ("bolson-arido",   "aridos", "construction aggregate bulk big bag", ["BOLSON"]),
    ("bolsita-arido",  "aridos", "small bag of sand", ["BOLSITA"]),
    ("polvo-piedra",   "aridos", "crushed stone dust pile", ["POLVO PIEDRA", "POLVO DE PIEDRA"]),
    ("piedra",         "aridos", "gravel crushed stone pile", ["PIEDRA"]),
    ("arena",          "aridos", "construction sand pile", ["ARENA"]),
    ("escombro",       "aridos", "construction rubble debris pile", ["ESCOMBRO"]),
    ("tosca",          "aridos", "soil fill dirt pile", ["TOSCA"]),

    # ---------------- CEMENTO / CAL ----------------
    ("cemento",        "cemento-cal", "portland cement bag", ["CEMENTO"]),
    ("cal",            "cemento-cal", "hydrated lime bag construction", ["CAL"]),
    ("yeso",           "cemento-cal", "gypsum plaster bag", ["YESO"]),
    ("hidralit",       "cemento-cal", "hydraulic lime bag", ["HIDRALIT", "HIDRAULICA"]),

    # ---------------- HIERROS ----------------
    ("malla",          "hierros", "welded wire mesh reinforcement", ["MALLA"]),
    ("vigueta",        "hierros", "concrete joist beam", ["VIGUETA", "VIGA"]),
    ("chapa",          "hierros", "galvanized steel sheet", ["CHAPA"]),
    ("perfil-angulo",  "hierros", "steel angle iron profile", ["ANGULO", "PERFIL", "OMEGA"]),
    ("planchuela",     "hierros", "steel flat bar", ["PLANCHUELA"]),
    ("cano-estruct",   "hierros", "square steel tube", ["ESTRUCTURAL", "TUBO"]),
    ("hierro",         "hierros", "steel rebar reinforcing bar", ["HIERRO", "CLAVADERA"]),

    # ---------------- LADRILLOS ----------------
    ("ladrillo-vidrio","ladrillos", "glass block brick", ["VIDRIO"]),
    ("ladrillo-telgopor","ladrillos", "eps foam insulation block", ["TELGOPOR"]),
    ("bloque",         "ladrillos", "concrete cinder block", ["BLOQUE", "HORMIGON"]),
    ("ladrillo-hueco", "ladrillos", "hollow clay brick block", ["HUECO"]),
    ("ladrillo",       "ladrillos", "red clay brick", ["LADRILLO"]),

    # ---------------- REFRACTARIOS ----------------
    ("tejuela-refra",  "refractarios", "refractory tile", ["TEJUELA", "ESQUINERO"]),
    ("tierra-refra",   "refractarios", "fire clay bag", ["TIERRA", "PEGAMENTO REF"]),
    ("ladrillo-refra", "refractarios", "fire brick refractory", ["REFRACTARI", "LADRILLO"]),

    # ---------------- PEGAMENTOS ----------------
    ("masilla-durlock","pegamentos", "drywall joint compound bucket", ["DURLOCK", "ANCLAFLEX"]),
    ("base-coat",      "pegamentos", "base coat plaster bag", ["BASE COAT"]),
    ("fino",           "pegamentos", "fine finishing plaster bag", ["FINO", "ULTRAFINO"]),
    ("mortero-mix",    "pegamentos", "ready mix mortar bag", ["MIX", "MORTERO", "PREMEZCLA", "CONCRETO"]),
    ("pegamento",      "pegamentos", "tile adhesive cement bag", ["PEGAMENTO", "WEBER"]),

    # ---------------- ADITIVOS ----------------
    ("hidrofugo",      "aditivos", "waterproofing additive bucket", ["HIDROFUGO"]),
    ("sika",           "aditivos", "construction adhesive sealant bottle", ["SIKA"]),
    ("aditivo",        "aditivos", "concrete additive bucket", ["ADITIVO", "ULTRAVINIL"]),

    # ---------------- ALAMBRES / CLAVOS ----------------
    ("tejido-romb",    "alambres", "chain link fence mesh", ["TEJIDO"]),
    ("clavo",          "alambres", "steel nails pile", ["CLAVO"]),
    ("alambre",        "alambres", "steel wire coil roll", ["ALAMBRE", "FARDO"]),

    # ---------------- PINTURAS ----------------
    ("membrana-rollo", "pinturas", "asphalt membrane roll roofing", ["MEMBRANA ROLLO", "ROBEROI", "ALUMINIZADO"]),
    ("membrana",       "pinturas", "roof waterproofing paint bucket", ["MEMBRANA"]),
    ("asfaltica",      "pinturas", "asphalt paint bucket", ["ASFALTICA"]),
    ("latex",          "pinturas", "latex wall paint bucket", ["LATEX", "LUMINOR"]),
    ("sintetico",      "pinturas", "enamel paint can", ["SINTETICO", "ESMALTE"]),
    ("antioxido",      "pinturas", "anti rust primer paint can", ["ANTIOXIDO", "CONVERTIDOR"]),
    ("barniz",         "pinturas", "wood varnish can", ["BARNIZ"]),
    ("enduido",        "pinturas", "wall filler paste bucket", ["ENDUIDO"]),
    ("fijador",        "pinturas", "sealer primer paint bucket", ["FIJADOR", "IMPREGNANTE"]),
    ("pintura",        "pinturas", "paint can bucket", ["PINTURA", "LATEX", "ENTONADOR"]),

    # ---------------- PINTURERÍA ----------------
    ("rodillo",        "pintureria", "paint roller", ["RODILLO"]),
    ("pincel",         "pintureria", "paint brush", ["PINCEL"]),
    ("lija",           "pintureria", "sandpaper sheet", ["LIJA"]),
    ("cinta-papel",    "pintureria", "masking tape roll", ["CINTA"]),
    ("masilla",        "pintureria", "wall filler putty", ["MASILLA"]),

    # ---------------- PLOMERÍA ----------------
    ("cano-estruct-p", "plomeria", "ppr fusion pipe", ["POLIPROPILENO", "FUSIOGAS", "TERMOFUSION"]),
    ("cano-cloacal",   "plomeria", "pvc sewer drainage pipe", ["AWADUCT", "CLOACAL", "DESCARGA"]),
    ("codo-pvc",       "plomeria", "pvc elbow fitting", ["CODO"]),
    ("curva-pvc",      "plomeria", "pvc pipe bend", ["CURVA"]),
    ("ramal-pvc",      "plomeria", "pvc tee branch fitting", ["RAMAL", "TEE"]),
    ("cupla",          "plomeria", "pvc coupling fitting", ["CUPLA", "UNION"]),
    ("reduccion",      "plomeria", "pvc pipe reducer", ["REDUCCION"]),
    ("niple",          "plomeria", "brass pipe nipple", ["NIPLE", "ESPIGA"]),
    ("valvula",        "plomeria", "plumbing ball valve", ["VALVULA", "LLAVE DE PASO", "LLAVE ESCLUSA"]),
    ("sifon",          "plomeria", "plumbing sink trap siphon", ["SIFON", "SOPAPA"]),
    ("rejilla",        "plomeria", "floor drain grate", ["REJILLA"]),
    ("canilla",        "plomeria", "water faucet tap", ["CANILLA", "GRIFO", "GRIFERIA"]),
    ("inodoro",        "plomeria", "ceramic toilet", ["INODORO"]),
    ("deposito",       "plomeria", "toilet cistern water tank", ["DEPOSITO", "MOCHILA"]),
    ("pileta",         "plomeria", "stainless steel kitchen sink", ["PILETA"]),
    ("ducha",          "plomeria", "shower head", ["DUCHA", "LLUVIA", "FLOR"]),
    ("flexible",       "plomeria", "flexible plumbing hose connector", ["FLEXIBLE"]),
    ("teflon",         "plomeria", "ptfe thread seal tape", ["TEFLON"]),
    ("manguera",       "plomeria", "garden hose roll", ["MANGUERA"]),
    ("tanque-agua",    "plomeria", "plastic water tank", ["TANQUE"]),
    ("tapa-pvc",       "plomeria", "pvc end cap fitting", ["TAPA", "TAPON"]),
    ("cano-pvc",       "plomeria", "white pvc pipe", ["CAÑO", "CANO", "PVC", "ROSCA", "BUJE"]),

    # ---------------- ELECTRICIDAD ----------------
    ("termica",        "electricidad", "miniature circuit breaker", ["TERMICA", "DISYUNTOR", "DIYUNTOR", "INTERRUPTOR DIF"]),
    ("tubo-led",       "electricidad", "led tube light", ["TUBO LED", "LISTON LED"]),
    ("reflector-led",  "electricidad", "led floodlight", ["REFLECTOR", "PROYECTOR"]),
    ("plafon-led",     "electricidad", "led ceiling panel light", ["PLAFON", "PANEL", "SPOT", "DICROIC", "TORTUGA", "ARTEFACTO", "VELADOR"]),
    ("lampara-led",    "electricidad", "led light bulb", ["LAMPARA", "FOCO", "BULBO", "DICROLED"]),
    ("cable",          "electricidad", "electrical cable wire roll", ["CABLE", "COAXIL"]),
    ("caja-luz",       "electricidad", "electrical junction box", ["CAJA"]),
    ("zapatilla",      "electricidad", "power strip extension", ["ZAPATILLA"]),
    ("jabalina",       "electricidad", "copper grounding rod", ["JABALINA", "PILAR", "MORCETO"]),
    ("ficha-ench",     "electricidad", "electrical plug socket", ["FICHA", "PORTALAMP", "SOQUETE", "TOMA", "MODULO", "BASTIDOR", "LLAVE"]),
    ("led-tira",       "electricidad", "led strip light", ["TIRA LED", "LED"]),

    # ---------------- BULONERÍA ----------------
    ("tirafondo",      "buloneria", "lag wood screw", ["TIRAFONDO"]),
    ("varilla-rosc",   "buloneria", "threaded steel rod", ["VARILLA ROSCADA"]),
    ("tornillo",       "buloneria", "metal screws", ["TORNILLO"]),
    ("tuerca",         "buloneria", "hex nuts steel", ["TUERCA"]),
    ("arandela",       "buloneria", "steel washers", ["ARANDELA", "GROWER", "PLANA"]),
    ("mariposa",       "buloneria", "wing nut butterfly anchor", ["MARIPOSA"]),
    ("tarugo",         "buloneria", "wall plug anchor", ["TARUGO"]),
    ("remache",        "buloneria", "aluminum rivets", ["REMACHE"]),
    ("abrazadera",     "buloneria", "metal hose clamp", ["ABRAZADERA", "GRAMPA", "PRECINTO"]),
    ("bulon",          "buloneria", "hex head bolt", ["BULON", "PERNO", "ESPARRAGO"]),

    # ---------------- HERRAJES ----------------
    ("bisagra",        "herrajes", "door hinge", ["BISAGRA"]),
    ("cerradura",      "herrajes", "door lock cylinder", ["CERRADURA", "CERROJO"]),
    ("candado",        "herrajes", "padlock", ["CANDADO"]),
    ("rueda",          "herrajes", "caster wheel", ["RUEDA"]),
    ("manija",         "herrajes", "door handle lever", ["MANIJA", "PICAPORTE", "MANIJON"]),
    ("pasador",        "herrajes", "barrel bolt latch", ["PASADOR", "PESTILLO", "FALLEBA", "GUIA", "CORREDIZA"]),

    # ---------------- HERRAMIENTAS ----------------
    ("pala",           "herramientas", "shovel", ["PALA"]),
    ("martillo",       "herramientas", "claw hammer", ["MARTILLO"]),
    ("cuchara-alb",    "herramientas", "masonry trowel", ["CUCHARA"]),
    ("fratacho",       "herramientas", "plastering float", ["FRATACHO"]),
    ("llana",          "herramientas", "finishing trowel", ["LLANA"]),
    ("serrucho",       "herramientas", "hand saw", ["SERRUCHO", "SIERRA"]),
    ("tenaza",         "herramientas", "carpenter pincers", ["TENAZA"]),
    ("maza",           "herramientas", "sledgehammer", ["MAZA"]),
    ("nivel",          "herramientas", "spirit level tool", ["NIVEL"]),
    ("plomada",        "herramientas", "plumb bob", ["PLOMADA"]),
    ("metro-cinta",    "herramientas", "tape measure", ["METRO", "FLEXOMETRO"]),
    ("espatula",       "herramientas", "putty knife spatula", ["ESPATULA"]),
    ("pinza",          "herramientas", "pliers tool", ["PINZA"]),
    ("mecha-broca",    "herramientas", "drill bit set", ["MECHA", "BROCA"]),
    ("disco-corte",    "herramientas", "cutting disc grinder", ["DISCO"]),
    ("balde",          "herramientas", "construction bucket", ["BALDE"]),
    ("carretilla",     "herramientas", "wheelbarrow", ["CARRETILLA"]),
    ("escalera",       "herramientas", "aluminum ladder", ["ESCALERA"]),
    ("guante",         "herramientas", "work gloves", ["GUANTE"]),
    ("amoladora",      "herramientas", "angle grinder", ["AMOLADORA"]),
    ("taladro",        "herramientas", "power drill", ["TALADRO"]),
    ("llave-herr",     "herramientas", "wrench spanner tool", ["LLAVE FRANCESA", "LLAVE TUBO", "LLAVE COMBINADA", "MACHO"]),
    ("destornillador", "herramientas", "screwdriver", ["DESTORNILL"]),
    ("herramienta",    "herramientas", "hand tools construction", ["AZADA", "ESCARDILLO", "RASTRILLO", "ZARANDA", "BARRETA", "ESCUADRA"]),

    # ---------------- ADHESIVOS / QUÍMICOS ----------------
    ("silicona",       "quimicos", "silicone sealant cartridge", ["SILICONA"]),
    ("sellador",       "quimicos", "construction sealant tube", ["SELLADOR", "SELL"]),
    ("grasa",          "quimicos", "grease lubricant tube", ["GRASA"]),
    ("aceite-lub",     "quimicos", "lubricating oil bottle", ["ACEITE", "LUBRICANTE", "WD"]),
    ("espuma-pu",      "quimicos", "polyurethane foam spray can", ["ESPUMA"]),
    ("adhesivo",       "quimicos", "adhesive glue tube", ["ADHESIVO", "POXI", "GOTITA", "PEGA", "CEMENTO PVC"]),

    # ---------------- FLETES ----------------
    ("flete",          "fletes", "construction delivery dump truck", ["FLETE", "ENVIO", "ACARREO"]),
]
