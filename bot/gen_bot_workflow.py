# -*- coding: utf-8 -*-
"""Genera el workflow de n8n para el asistente Abril (Evolution API)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

PROMPT = open(os.path.join(HERE, "abril-system-prompt.md"), encoding="utf-8").read()

PARSE_CODE = r"""
// ====== Abril · parseo + handoff (Micaela interrumpe / Abril se calla) ======
const cfg = $('Config').first().json;
const PAUSE_MIN = Number(cfg.pauseMinutes) || 30;
const RESUME_KW = String(cfg.resumeKeyword || '#abril').toLowerCase().trim();
const CATALOG_URL = cfg.catalogUrl;

const store = $getWorkflowStaticData('global');
store.paused  = store.paused  || {};   // { jid: timestamp-fin-pausa }
store.botSent = store.botSent || [];    // ids de mensajes que mandó Abril

const wh   = $('Webhook').first().json;
const body = wh.body || wh;
if (body.event && body.event !== 'messages.upsert') return [];
let data = body.data; if (Array.isArray(data)) data = data[0]; data = data || {};
const key      = data.key || {};
const jid      = key.remoteJid || '';
const fromMe   = !!key.fromMe;
const msgId    = key.id || '';
const m        = data.message || {};
const text     = String(m.conversation || (m.extendedTextMessage && m.extendedTextMessage.text) || '').trim();
const pushName = data.pushName || '';
const now = Date.now();

// descartar: grupos, estados, sin texto
if (!jid || jid.endsWith('@g.us') || jid === 'status@broadcast' || !text) return [];

// ---- mensajes salientes (los manda el celu: Abril o Micaela) ----
if (fromMe) {
  if (store.botSent.includes(msgId)) return [];          // eco del propio Abril -> ignorar
  if (text.toLowerCase() === RESUME_KW) {                 // Micaela devuelve el control
    delete store.paused[jid];
    return [];
  }
  store.paused[jid] = now + PAUSE_MIN * 60 * 1000;        // Micaela tomó la charla -> pausar Abril
  return [];
}

// ---- mensaje del cliente ----
const until = store.paused[jid] || 0;
if (until && now < until) return [];                      // Micaela está atendiendo -> Abril callada
if (until && now >= until) delete store.paused[jid];      // venció la pausa -> Abril retoma

// precargar catálogo una vez (lo usa la herramienta buscarPrecio)
if (!store.catalog) {
  try { const r = await this.helpers.httpRequest({ url: CATALOG_URL, json: true });
        store.catalog = r.productos || r; }
  catch (e) { store.catalog = []; }
}

return [{ json: { chatId: jid, number: jid.split('@')[0], text, pushName, sessionId: jid } }];
"""

BUSCAR_CODE = r"""
const CATALOG_URL = 'https://grupoimpactomkt-pixel.github.io/corralon-2-de-abril/catalog.json';
const store = $getWorkflowStaticData('global');
let cat = store.catalog;
if (!cat || !cat.length) {
  try {
    if (this.helpers && this.helpers.httpRequest) {
      const r = await this.helpers.httpRequest({ url: CATALOG_URL, json: true });
      cat = r.productos || r;
    } else {
      const r = await fetch(CATALOG_URL); cat = (await r.json()).productos;
    }
    store.catalog = cat;
  } catch (e) { return 'No pude acceder al catálogo ahora; que lo confirme Micaela.'; }
}
const norm = s => (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
const stop = ['del','los','las','por','con','para','que','cuanto','sale','precio','tenes','tienen','hay','una','uno','el','la','de','y','me','mi','por','x'];
const terms = norm(query).split(/\s+/).filter(t => t.length >= 2 && !stop.includes(t));
if (!terms.length) return 'Decime qué producto buscás.';
const scored = [];
for (const p of cat) { const n = norm(p.n); let s = 0; for (const t of terms) if (n.includes(t)) s++; if (s) scored.push([s, p]); }
scored.sort((a,b) => b[0]-a[0]);
if (!scored.length) return 'No lo encontré en el catálogo; que lo confirme Micaela.';
return scored.slice(0,6).map(x => `${x[1].n} | lista $${x[1].p} | web efectivo $${x[1].w} | ${x[1].c}`).join('\n');
"""

AGENDAR_CODE = r"""
let d = {}; try { d = JSON.parse(query); } catch (e) {
  return 'Para agendar pasame un JSON con: nombre, direccion, dia, franja, detalle.';
}
const store = $getWorkflowStaticData('global');
store.entregas = store.entregas || [];
const reg = { creado: new Date().toISOString(), nombre: d.nombre||'', direccion: d.direccion||'',
              dia: d.dia||'', franja: d.franja||'', detalle: d.detalle||'' };
store.entregas.push(reg);
return `Entrega agendada ✅ ${reg.dia} ${reg.franja} en ${reg.direccion}. Micaela la confirma.`;
"""

REGISTRAR_CODE = r"""
const store = $getWorkflowStaticData('global'); store.botSent = store.botSent || [];
const resp = $json; const id = resp && resp.key && resp.key.id;
if (id) { store.botSent.push(id); if (store.botSent.length > 300) store.botSent = store.botSent.slice(-300); }
return $input.all();
"""

def node(name, ntype, tv, pos, params, creds=None, extra=None):
    n = {"parameters": params, "id": name.lower().replace(' ', '-'),
         "name": name, "type": ntype, "typeVersion": tv, "position": pos}
    if creds: n["credentials"] = creds
    if extra: n.update(extra)
    return n

nodes = [
    node("Webhook", "n8n-nodes-base.webhook", 2, [0, 300],
         {"httpMethod": "POST", "path": "abril-whatsapp", "responseMode": "onReceived"},
         extra={"webhookId": "abril-whatsapp"}),

    None,  # placeholder Config (se inyecta abajo)

    node("Abril (parse & gate)", "n8n-nodes-base.code", 2, [440, 300], {"jsCode": PARSE_CODE}),

    node("Abril", "@n8n/n8n-nodes-langchain.agent", 2, [700, 300], {
        "promptType": "define", "text": "={{ $json.text }}",
        "options": {"systemMessage": PROMPT}}),

    None,  # placeholder Modelo (se inyecta abajo)

    node("Memoria (por chat)", "@n8n/n8n-nodes-langchain.memoryBufferWindow", 1.3, [760, 520],
         {"sessionIdType": "customKey", "sessionKey": "={{ $json.sessionId }}", "contextWindowLength": 12}),

    node("buscarPrecio", "@n8n/n8n-nodes-langchain.toolCode", 1.1, [900, 520], {
        "name": "buscarPrecio",
        "description": "Busca productos del catálogo del corralón y devuelve precio de lista y precio web efectivo (15% OFF). Input: el nombre o palabras del producto (ej 'cemento avellaneda 25').",
        "language": "javaScript", "jsCode": BUSCAR_CODE}),

    node("agendarEntrega", "@n8n/n8n-nodes-langchain.toolCode", 1.1, [1040, 520], {
        "name": "agendarEntrega",
        "description": "Agenda una entrega a domicilio. Input: un JSON string con campos nombre, direccion, dia, franja, detalle.",
        "language": "javaScript", "jsCode": AGENDAR_CODE}),

    node("Enviar (Evolution)", "n8n-nodes-base.httpRequest", 4.2, [1080, 300], {
        "method": "POST",
        "url": "={{ $('Config').first().json.evolutionUrl }}/message/sendText/{{ $('Config').first().json.instance }}",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "apikey", "value": "={{ $('Config').first().json.apiKey }}"},
            {"name": "Content-Type", "value": "application/json"}]},
        "sendBody": True, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ number: $('Abril (parse & gate)').first().json.number, text: $json.output }) }}",
        "options": {}}),

    node("Registrar envío", "n8n-nodes-base.code", 2, [1300, 300], {"jsCode": REGISTRAR_CODE}),
]

connections = {
    "Webhook": {"main": [[{"node": "Config", "type": "main", "index": 0}]]},
    "Config": {"main": [[{"node": "Abril (parse & gate)", "type": "main", "index": 0}]]},
    "Abril (parse & gate)": {"main": [[{"node": "Abril", "type": "main", "index": 0}]]},
    "Abril": {"main": [[{"node": "Enviar (Evolution)", "type": "main", "index": 0}]]},
    "Enviar (Evolution)": {"main": [[{"node": "Registrar envío", "type": "main", "index": 0}]]},
    "Modelo (OpenAI)": {"ai_languageModel": [[{"node": "Abril", "type": "ai_languageModel", "index": 0}]]},
    "Memoria (por chat)": {"ai_memory": [[{"node": "Abril", "type": "ai_memory", "index": 0}]]},
    "buscarPrecio": {"ai_tool": [[{"node": "Abril", "type": "ai_tool", "index": 0}]]},
    "agendarEntrega": {"ai_tool": [[{"node": "Abril", "type": "ai_tool", "index": 0}]]},
}

def config_node(creds):
    return node("Config", "n8n-nodes-base.set", 3.4, [220, 300], {
        "includeOtherInputFields": True,
        "assignments": {"assignments": [
            {"id": "a1", "name": "evolutionUrl", "type": "string", "value": creds["evolutionUrl"]},
            {"id": "a2", "name": "instance", "type": "string", "value": creds["instance"]},
            {"id": "a3", "name": "apiKey", "type": "string", "value": creds["apiKey"]},
            {"id": "a4", "name": "pauseMinutes", "type": "number", "value": 30},
            {"id": "a5", "name": "resumeKeyword", "type": "string", "value": "#abril"},
            {"id": "a6", "name": "catalogUrl", "type": "string",
             "value": "https://grupoimpactomkt-pixel.github.io/corralon-2-de-abril/catalog.json"},
        ]}})

def model_node(creds):
    return node("Modelo (OpenAI)", "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2, [620, 520],
                {"model": {"__rl": True, "mode": "list", "value": creds.get("openAiModel", "gpt-5.4-mini")},
                 "options": {"temperature": 0.4}},
                creds={"openAiApi": {"id": creds.get("openAiCredId", "REEMPLAZAR"),
                                     "name": creds.get("openAiCredName", "OpenAI account")}})

PLACEHOLDER = {"evolutionUrl": "https://TU-EVOLUTION-API", "instance": "TU-INSTANCIA",
               "apiKey": "TU-APIKEY-EVOLUTION"}

def build(creds):
    ns = []
    seen_none = 0
    for n in nodes:
        if n is None:
            ns.append(config_node(creds) if seen_none == 0 else model_node(creds))
            seen_none += 1
        else:
            ns.append(n)
    return {"name": "Corralón 2 de Abril · Asistente Abril (WhatsApp)",
            "nodes": ns, "connections": connections,
            "settings": {"executionOrder": "v1"}, "active": False, "pinData": {}}

# 1) versión committeable (placeholders, sin secretos)
out = os.path.join(HERE, "abril-n8n-workflow.json")
json.dump(build(PLACEHOLDER), open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK (placeholders):", out)

# 2) versión local LISTA (con credenciales) si existe bot/.secrets.json -> NO se sube a git
sec = os.path.join(HERE, ".secrets.json")
if os.path.exists(sec):
    creds = json.load(open(sec, encoding="utf-8"))
    outl = os.path.join(HERE, "abril-n8n-workflow.local.json")
    json.dump(build(creds), open(outl, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK (con credenciales):", outl)
