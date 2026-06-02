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
const store = $getWorkflowStaticData('global');
const cat = store.catalog || [];
const norm = s => (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
const terms = norm(query).split(/\s+/).filter(Boolean);
if (!terms.length) return 'Decime qué producto buscás.';
const hits = cat.filter(p => { const n = norm(p.n); return terms.every(t => n.includes(t)); }).slice(0, 8);
if (!hits.length) return 'No lo encontré en el catálogo; que lo confirme Micaela.';
return hits.map(p => `${p.n} | lista $${p.p} | web efectivo $${p.w} | ${p.c}`).join('\n');
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

    node("Config", "n8n-nodes-base.set", 3.4, [220, 300], {
        "includeOtherInputFields": True,
        "assignments": {"assignments": [
            {"id": "a1", "name": "evolutionUrl", "type": "string", "value": "https://TU-EVOLUTION-API"},
            {"id": "a2", "name": "instance", "type": "string", "value": "TU-INSTANCIA"},
            {"id": "a3", "name": "apiKey", "type": "string", "value": "TU-APIKEY-EVOLUTION"},
            {"id": "a4", "name": "pauseMinutes", "type": "number", "value": 30},
            {"id": "a5", "name": "resumeKeyword", "type": "string", "value": "#abril"},
            {"id": "a6", "name": "catalogUrl", "type": "string",
             "value": "https://grupoimpactomkt-pixel.github.io/corralon-2-de-abril/catalog.json"},
        ]}}),

    node("Abril (parse & gate)", "n8n-nodes-base.code", 2, [440, 300], {"jsCode": PARSE_CODE}),

    node("Abril", "@n8n/n8n-nodes-langchain.agent", 1.7, [700, 300], {
        "promptType": "define", "text": "={{ $json.text }}",
        "options": {"systemMessage": PROMPT}}),

    node("Claude (modelo)", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.2, [620, 520],
         {"model": "claude-3-5-haiku-20241022", "options": {"temperature": 0.4}},
         creds={"anthropicApi": {"id": "REEMPLAZAR", "name": "Anthropic account"}}),

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
    "Claude (modelo)": {"ai_languageModel": [[{"node": "Abril", "type": "ai_languageModel", "index": 0}]]},
    "Memoria (por chat)": {"ai_memory": [[{"node": "Abril", "type": "ai_memory", "index": 0}]]},
    "buscarPrecio": {"ai_tool": [[{"node": "Abril", "type": "ai_tool", "index": 0}]]},
    "agendarEntrega": {"ai_tool": [[{"node": "Abril", "type": "ai_tool", "index": 0}]]},
}

wf = {"name": "Corralón 2 de Abril · Asistente Abril (WhatsApp)",
      "nodes": nodes, "connections": connections,
      "settings": {"executionOrder": "v1"}, "active": False, "pinData": {}}

out = os.path.join(HERE, "abril-n8n-workflow.json")
json.dump(wf, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK:", out, "|", len(nodes), "nodos")
