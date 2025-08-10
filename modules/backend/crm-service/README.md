# CRM Service (MVP)

Servicio ligero de CRM para segmentar usuarios, crear campañas y registrar notificaciones basadas en preferencias y en el historial de compras.

## Funcionalidades

- Segmentos con filtros sencillos sobre `users.preferences` y `purchase_history`:
  - `last_days`, `min_total_spent`, `min_num_purchases`, `stores_in`, `is_market_store`, `preferences_contains`
- Campañas asociadas a uno o varios segmentos
- Previsualización de usuarios objetivo de un segmento o campaña
- Despacho de campaña: genera notificaciones en estado `queued` por usuario objetivo
- Registro de notificaciones y estados (`queued`, `sent`, `failed`)

## Endpoints principales

- `POST /segments` - Crear segmento
- `GET /segments` - Listar segmentos
- `GET /segments/{segment_id}` - Obtener segmento
- `POST /segments/{segment_id}/preview-users` - Previsualizar usuarios de un segmento
- `POST /campaigns` - Crear campaña
- `GET /campaigns` - Listar campañas
- `GET /campaigns/{campaign_id}` - Obtener campaña
- `POST /campaigns/{campaign_id}/preview-users` - Previsualizar usuarios objetivo (unión de segmentos)
- `POST /campaigns/{campaign_id}/dispatch` - Despachar campaña (genera notificaciones `queued`)
- `GET /notifications` - Listar notificaciones
- `POST /notifications/{notification_id}/mark-sent` - Marcar notificación como enviada

### IA (generación de texto)
- `POST /ai/generate` (admin): genera texto usando Llama vía Ollama. Envía `{ prompt, system?, temperature?, max_tokens? }`, devuelve `{ text }`.
  - Variables de entorno: `OLLAMA_HOST` (por defecto `http://ollama:11434`), `LLM_MODEL` (por defecto `llama3.2:1b-instruct`).

## Configuración

Variables de entorno:

- `DATABASE_URL`: URL de conexión a PostgreSQL (mismo cluster que el resto de servicios)
- `HOST` (opcional, por defecto `0.0.0.0`)
- `PORT` (opcional, por defecto `8006`)
- `LOG_LEVEL` (opcional)

## Desarrollo local

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8006
```

## Notas

- Este servicio no envía notificaciones reales en el MVP; registra la intención de envío en la tabla `notifications` para su posterior procesamiento por un worker/servicio externo.
- Se definen modelos mínimos locales de `users` y `purchase_history` para realizar consultas de segmentación.


