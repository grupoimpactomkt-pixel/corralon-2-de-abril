# Corralón 2 de Abril — Catálogo digital

Catálogo web de materiales para la construcción con **carrito y pedido por WhatsApp**,
inspirado en la lógica de la app de menús `menu.byroncode.com` pero adaptado a un corralón.

Es un **sitio estático** (HTML + CSS + JS, sin backend). Se abre con doble clic en
`index.html` o se sube tal cual a cualquier hosting (Netlify, Vercel, GitHub Pages, etc.).

## Contenido

- **3.792 productos** en **19 rubros** (cemento, áridos, hierros, ladrillos, pinturas,
  membranas, plomería/PVC, electricidad, herramientas, bulonería, herrajes, fletes, etc.)
  cargados desde las dos listas de precios.
- Imagen representativa por rubro (descargadas con licencia Creative Commons vía Openverse).
- Búsqueda en vivo, navegación por categorías, carrito persistente (localStorage) y
  armado automático del pedido por WhatsApp.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | Estructura de la página |
| `styles.css` | Estilos / identidad visual de la marca |
| `app.js` | Lógica: catálogo, búsqueda, carrito, checkout WhatsApp |
| `config.js` | **Datos del negocio (editá esto)** |
| `data.js` | Catálogo generado (`window.CATALOG`) |
| `assets/` | Logo y emblema (SVG) |
| `img/cat/` | Imágenes por categoría |
| `build_data.py` | Regenera `data.js` desde los Excel |
| `fetch_images.py` | Vuelve a bajar las imágenes por categoría |

## ⚙️ Personalizar (importante)

Editá **`config.js`**:

1. **`whatsapp`** → poné el número real del corralón en formato internacional sin `+`
   ni espacios. Ej. celular argentino: `549` + característica sin `0` + número sin `15`.
   Es lo único imprescindible para que los pedidos lleguen al WhatsApp correcto.
2. `address`, `hours`, `phoneDisplay`, `instagram`, `rating`, `reviews` → datos reales.

## Actualizar precios / productos

1. Reemplazá los Excel en la carpeta padre (`../lista precios ...xlsx`).
2. Ejecutá:
   ```
   python build_data.py     # regenera data.js
   python fetch_images.py   # (opcional) refresca imágenes por rubro
   ```

## Probar localmente

Doble clic en `index.html`, **o** servidor local:
```
python -m http.server 8000
# abrir http://localhost:8000
```

## Notas

- Los precios son de lista y **no incluyen flete**; el pedido por WhatsApp deja en claro
  que el monto es estimado y sujeto a confirmación.
- El rubro **"Varios"** agrupa ítems que no encajan en una categoría clara.
- Las imágenes son representativas por rubro (no foto exacta de cada producto), según lo definido.
