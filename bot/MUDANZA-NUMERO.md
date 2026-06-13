# Mudar Abril a un número de WhatsApp nuevo (Corralón 2 de Abril)

Cuando Micaela consiga el **número dedicado** del negocio, mover Abril ahí es rápido y **no se pierde nada** (todo vive en Supabase: catálogo, pedidos, usuarios, mensajes, sinónimos).

## Pasos
1. **Conseguir el número** (chip dedicado del negocio, NO el personal de Micaela; que sea recuperable).
2. **Reconectar Evolution a ese número**:
   - En el panel de Evolution, en la instancia `ASISTENTEDEMOGERMAN` (o crear una nueva instancia para el cliente).
   - Escanear el QR desde el WhatsApp del número nuevo.
3. **Actualizar el número del negocio** donde corresponda:
   - `config.js` del sitio (`whatsapp`) → el número que ven los clientes para pedir.
   - Tabla `tenants`, `config.whatsapp` del tenant 1 (opcional, informativo).
4. **No hace falta tocar la lógica**: el Router, las herramientas, los roles y la data siguen igual.
5. **Probar**: mandar un mensaje de prueba al número nuevo y confirmar que Abril responde y que `mensajes` loguea.

## Notas
- Los **roles** (Micaela super_admin, Germán soporte) están atados al número de **cada persona**, no al número del bot → siguen funcionando igual tras la mudanza.
- Si en el futuro se quiere un **proyecto Supabase dedicado** para Corralón: cargar `infra/schema.sql` en el proyecto nuevo, migrar las filas del tenant 1 y repuntar las credenciales. Hoy NO hace falta (multi-tenant compartido alcanza).
- Tener un **número de respaldo** preparado: como la data vive en Supabase, cambiar de número = reconectar y seguir.
