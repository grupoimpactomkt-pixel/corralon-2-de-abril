# ESTUAPP — Reseña del proyecto y petición de recomendaciones

> Documento para compartir con otro proyecto / desarrollador / IA y pedir una **segunda opinión técnica y de negocio**. Resume qué es, qué objetivos tiene, cómo está construido hoy, qué riesgos vemos y en qué puntos queremos recomendación.

---

## 1. Resumen ejecutivo

**ESTUAPP** (de la agencia **Grupo Impacto**) es un negocio de **asistentes de WhatsApp con IA, multi-cliente**. El producto se llama **"Abril"**: una vendedora virtual que atiende por WhatsApp, **cotiza con precios reales**, arma el pedido, agenda entregas, **cierra la venta dejándola lista para una persona**, y se calla cuando un humano toma la conversación.

El **cliente insignia** (primero confirmado y pagando) es el **Corralón 2 de Abril**, un corralón/ferretería real de Mar del Plata (Argentina), con ~3.800 productos.

Hay además un **modo demo de prospección**: con una palabra clave, Abril "se transforma" en cualquier otro comercio a partir de su lista de precios (texto, PDF, foto o audio), para mostrarle a un prospecto en vivo cómo lo atendería su propio bot.

---

## 2. Objetivos

### De negocio
- **Vender más** para el comercio cliente: que Abril atienda 24/7, cotice al toque y deje el pedido cocinado para que el dueño solo confirme.
- **Ingreso recurrente para la agencia**: un Abril por cliente (modelo tipo suscripción).
- **Prospección veloz**: cerrar nuevos clientes mostrándoles una demo en vivo personalizada con su propia lista.
- **Que lo maneje un no-técnico**: el dueño/vendedor edita productos, precios y sinónimos desde el WhatsApp, sin tocar nada técnico.

### Técnicos / de producto
- Que **no parezca un bot**: tono humano argentino, breve, empuja al cierre, nunca se equivoca en precios/números.
- **Costo casi cero**: todo en planes gratuitos / pago por uso. No superar el gasto actual de infraestructura.
- **Multi-cliente ordenado**: varios comercios y demos conviviendo, separados, sin pisarse.
- **Handoff humano impecable**: cuando la persona interviene, el bot frena y luego retoma con contexto.

---

## 3. Modelo de negocio: "calientes" vs "frías"

- **Clientes calientes** = comercios reales que pagan (ej. Corralón 2 de Abril). Datos limpios, aislados.
- **Demos frías** = prospección en vivo. Abril simula al comercio del prospecto con su lista. Datos efímeros, no deben ensuciar a los clientes reales.

---

## 4. Arquitectura actual

**Stack:**
- **Frontend**: sitio de catálogo estático (HTML/CSS/JS) en **GitHub Pages**. ~3.800 productos en `catalog.json` generado desde Excel. Pedido por WhatsApp, 15% OFF efectivo.
- **WhatsApp**: **Evolution API** (basada en Baileys, **no oficial**) corriendo en **Easypanel**.
- **Orquestación**: **n8n** (self-hosted en Easypanel). Un nodo "Router" (Code) hace el parseo/ruteo y un **agente LangChain ("Abril")** con herramientas.
- **IA**: **OpenAI** — modelo de chat para Abril, **Whisper** para audios, **GPT-4o visión** para fotos de listas, **text-embedding-3-small** para RAG.
- **Datos**: **Supabase** (proyecto "asistente-madre"), Postgres + **pgvector** para RAG. Diseño **multi-tenant** por `tenant_id`.

**Flujo de un mensaje entrante (simplificado):**
```
WhatsApp → Evolution (webhook) → n8n Router (Code node):
  - ¿es de la persona (vendedor) escribiendo a mano? → pausa Abril 15 min
  - ¿es audio? → lo transcribe (Whisper) y lo trata como texto
  - ¿es imagen? → responde "lo chequea Micaela" y pausa
  - ¿es comando admin (#...) del número del dueño? → edita productos/precios/sinónimos
  - ¿modo demo? → máquina de estados (nombre → brief → lista → vende como ese comercio)
  - si no → arma el systemPrompt + lee el historial real del chat → agente Abril
Agente Abril (con herramientas) → respuesta → Evolution → WhatsApp
```

**Herramientas del agente:**
- `buscarPrecio`: busca en el catálogo (base estático **+ capa editable en Supabase + sinónimos**) y devuelve precio lista y precio web efectivo.
- `consultarInfo`: RAG sobre la base de conocimiento del comercio (envíos, horarios, qué sirve para cada necesidad).
- `agendarEntrega`: agenda envío a domicilio.
- `guardarPedido`: registra el pedido confirmado con número y (opcional) avisa al vendedor.

---

## 5. Funciones implementadas (Abril)

- **Venta con precios reales** + armado de pedido con totales (lista y web efectivo, ahorro).
- **Formas de pago**: efectivo (15% OFF al retirar), transferencia (alias bancario, pide comprobante, una persona verifica), débito/crédito.
- **Flete por barrio** (lo busca en la lista) y agenda de entregas.
- **Handoff humano**: la dueña (Micaela) interviene desde el teléfono → Abril se calla **15 min** y luego **retoma leyendo la conversación previa real** (incluido lo que escribió la persona). Palabra clave `#abril` para devolver el control antes.
- **Audios**: transcribe y responde como si fuera texto.
- **Imágenes**: avisa "ahí lo chequea Micaela y te contesta" y pausa (las fotos las ve un humano).
- **Modo demo** (`IMPACTODEMO` / `SALIRDEMO`): se vuelve otro comercio desde su lista (texto/PDF/foto/audio).
- **Superadmin por WhatsApp** (bloqueado al número del dueño): `#buscar`, `#precio`, `#agregar`, `#borrar`, `#sinonimo`. Edita la capa de productos sin tocar el Excel base.
- **Persona**: breve, humana, argentina, sin signos de apertura (¿¡), pocos emojis, empuja al cierre, esquiva temas ajenos.
- `@info`: resumen de funciones.

---

## 6. Datos / diseño multi-tenant

Un solo proyecto Supabase con todo separado por `tenant_id`:
- `tenants` — maestro de comercios (Corralón = tenant 1; demos y futuros clientes = otros tenants).
- `kb` — base de conocimiento (RAG, pgvector) por tenant. RPC `match_kb` filtra por tenant.
- `pedidos` — ventas por tenant.
- `productos` — **capa editable** (alta/edición/borrado) que se mezcla sobre el catálogo base estático.
- `aliases` — sinónimos de búsqueda (ej. "ceresita" → "hidrofugo").
- `demo_tenants` — sesiones de demo en vivo (por chat_id, efímeras).
- `mensajes` — historial (auditoría / ventas perdidas) [tabla creada, aún no poblada en automático].

---

## 7. Estado actual

- Corralón **en producción de prueba**: hay tráfico real de clientes testeando.
- Migración a Supabase propio de la agencia **completa y verificada**.
- Audio, imágenes, handoff con contexto, superadmin y sinónimos **funcionando y probados**.
- La marca **confirmó** ser cliente; **falta el número de WhatsApp definitivo** para el cutover final a su instancia/proyecto.

---

## 8. Riesgos y limitaciones conocidas

1. **WhatsApp no oficial (Evolution/Baileys)**: riesgo de baneo del número. Crítico cuando hay clientes pagando.
2. **Doble fuente de verdad del catálogo**: la **web** lee el Excel estático; el **bot** lee Excel base + capa editable en Supabase. Si el dueño edita un precio por WhatsApp, **el bot cambia pero la web no** hasta reconstruir. Hay riesgo de divergencia.
3. **Límite de Supabase free**: 2 proyectos activos por organización. Condiciona "un proyecto por cliente".
4. **Lectura de historial por mensaje** (a Evolution): simple y fiel, pero puede no escalar en chats muy largos / muchos clientes.
5. **Memoria del agente**: el buffer de n8n no persiste los mensajes manuales del vendedor (por eso leemos el historial de Evolution).
6. **Edición de precios por chat**: cómoda para retoques, engorrosa/riesgosa para cambios masivos.
7. **Dependencia de un nodo Code grande** (el Router) y de credenciales embebidas en nodos.

---

## 9. Decisiones abiertas (dónde queremos recomendación)

1. **¿Migrar a la API oficial de WhatsApp (Cloud API)** para los clientes que pagan, y dejar Evolution solo para demos? ¿Costo/beneficio?
2. **¿Cómo escalar a N clientes?** ¿Proyecto Supabase dedicado por cliente (aislamiento, pero límite de 2 en free) vs. un proyecto compartido multi-tenant? ¿Cuándo conviene cada uno?
3. **¿Unificar la fuente de verdad del catálogo** (web + bot leyendo la misma base) para eliminar la divergencia? ¿Mover los 3.800 productos a Supabase y que la web lea de ahí?
4. **¿Mejor UX de administración** para el dueño: comandos por WhatsApp vs. un panel web simple? ¿Híbrido?
5. **¿Persistir historial de conversaciones** (tabla `mensajes`) y usarlo para memoria/analítica de ventas perdidas?
6. **Modelo de precios de la agencia** hacia sus clientes (suscripción, setup + mensual, por volumen).
7. **Robustez/observabilidad**: manejo de errores, reintentos, monitoreo, backups antes de tener datos reales serios.
8. **Próximas funciones de alto impacto** para un corralón: calculadora de materiales (m² → bolsas/ladrillos), foto→cotización, aviso de pedidos al vendedor, recordatorio de entregas.

---

## 10. La petición concreta

> Necesitamos una **revisión crítica y recomendaciones priorizadas** sobre el sistema descrito, con foco en:
> 1. **Escalabilidad multi-cliente** manteniendo costo casi nulo (planes free / pago por uso).
> 2. **Riesgo de WhatsApp no oficial** y si/ cómo migrar a la API oficial.
> 3. **Unificar el catálogo** (web + bot) en una sola fuente de verdad sin romper lo que funciona.
> 4. **UX de administración** para un dueño no técnico.
> 5. **Qué es frágil hoy** y debería endurecerse antes de sumar más clientes.
>
> Para cada punto: recomendación concreta, esfuerzo estimado, y qué romper/no romper. Priorizar por impacto vs. esfuerzo. Asumir que el equipo es chico y el presupuesto, mínimo.
