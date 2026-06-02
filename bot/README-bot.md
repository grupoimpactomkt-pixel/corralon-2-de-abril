# Asistente "Abril" — WhatsApp (n8n + Evolution API)

Bot de atención y venta del **Corralón 2 de Abril**. Responde al instante, **cotiza con los precios
reales** (catálogo + 15% web), arma el pedido, **agenda entregas**, y deja la venta lista para que
**Micaela** la cierre. Incluye **handoff**: cuando Micaela escribe, Abril se calla.

## Archivos
- `abril-n8n-workflow.json` — workflow para **importar en n8n**.
- `abril-system-prompt.md` — la personalidad/instrucciones de Abril (editable).
- `gen_bot_workflow.py` — regenera el workflow si cambiás el prompt.
- `../catalog.json` — catálogo (precios) que consulta Abril (se publica con el sitio).

## Requisitos
1. **n8n** (cloud o self-host).
2. **Evolution API** con una instancia conectada al WhatsApp (el celu demo que me vas a pasar).
3. Una credencial de **modelo IA** en n8n (por defecto **Anthropic/Claude**; se puede cambiar a OpenAI).

## Instalación (paso a paso)
1. **Importá** `abril-n8n-workflow.json` en n8n (Workflows → Import from File).
2. Abrí el nodo **Config** y completá:
   - `evolutionUrl` → URL de tu Evolution API (ej. `https://miapi.com`).
   - `instance` → nombre de la instancia.
   - `apiKey` → API key de Evolution.
   - `pauseMinutes` → minutos que Abril queda en silencio cuando Micaela interviene (default 30).
   - `resumeKeyword` → palabra que escribe Micaela para devolverle el control a Abril (default `#abril`).
   - `catalogUrl` → ya viene apuntando al catálogo publicado.
3. En el nodo **Claude (modelo)** cargá tu credencial de Anthropic (o reemplazá el nodo por OpenAI).
4. **Activá** el workflow. Copiá la **Production URL** del nodo *Webhook*
   (algo como `https://TU-N8N/webhook/abril-whatsapp`).
5. En **Evolution API**, configurá el **webhook** de la instancia apuntando a esa URL, con el evento
   **`MESSAGES_UPSERT`** activado.
6. Mandá un WhatsApp al número demo → Abril responde 🎉.

## Cómo funciona el handoff (Micaela interrumpe)
- Cuando **Micaela escribe manualmente** desde el celular en un chat, Abril **deja de responder** en
  ese chat por `pauseMinutes` (default 30').
- Abril **retoma sola** cuando vence ese tiempo, **o** cuando Micaela escribe la palabra `#abril`.
- Abril **nunca pisa** a Micaela: detecta sus propios mensajes (no se confunde con los de ella).

## Personalización
- **Qué dice / cómo vende:** editá `abril-system-prompt.md` y pegá el texto en el nodo *Abril*
  (campo *System Message*). O corré `python gen_bot_workflow.py` para regenerar el JSON.
- **Descuento web:** está en el prompt y en `catalog.json` (campo `w` = precio web). Para cambiarlo,
  ajustá el factor en `build_data`/`catalog.json` y el texto del prompt.
- **Tiempo de pausa / palabra de retomar:** nodo *Config*.

## Agenda de entregas
La herramienta `agendarEntrega` guarda los turnos (nombre, dirección, día, franja, detalle).
En esta versión quedan en la memoria del workflow. **Recomendado:** para que Micaela las vea en una
planilla, reemplazá la herramienta por un nodo **Google Sheets (Append)** — está documentado dónde
en el nodo `agendarEntrega`. (Te lo dejo armado cuando me pases la cuenta de Google del corralón.)

## RAG (conocimiento + búsqueda semántica) — YA INSTALADO
Abril es **híbrida**: precios por catálogo exacto + un RAG para conocimiento y necesidades.
- **Conocimiento:** `abril-conocimiento.md` → se genera `kb.json` (publicado) → se vectoriza con embeddings
  OpenAI (`text-embedding-3-small`) en la tabla **`corralon_kb`** de tu Supabase pgvector (aislada de Fiorensa).
- **Herramienta `consultarInfo`:** sub-workflow n8n *"CORRALON RAG retrieve"* que embebe la pregunta y busca por
  similitud (`embedding <=> query`). Conectada al agente como tool.
- **Re-ingestar** (si editás el conocimiento): actualizá `abril-conocimiento.md`, regenerá `kb.json`, publicalo,
  y activá+dispará una vez el workflow *"CORRALON RAG ingesta"* (hace TRUNCATE + re-embeddings + insert).
- Workflows en n8n: Abril `bJVDxLNXQLgS7yuK`, retrieve `OSWrQ3QEeYPEHvwE`, ingesta `PUd3Mn74wOzS0PAP` (inactivo).

## Notas
- El cuerpo del `sendText` de Evolution puede variar según la versión (`{number, text}` vs
  `{number, textMessage:{text}}`). Si no envía, ajustá el `jsonBody` del nodo *Enviar (Evolution)*.
- Si al importar n8n te marca una versión de nodo distinta, dejá que la actualice (auto-migra).
- Modelo por defecto: `claude-3-5-haiku` (rápido y barato). Para respuestas más finas, cambialo a Sonnet.
