# Notification Sender Service

Servicio para enviar notificaciones a través de diferentes canales (WebPush, Android, iOS).

## Arquitectura

El servicio utiliza un patrón de adapters para manejar diferentes canales de notificación:

- **WebPush Adapter**: Implementado completamente para notificaciones push web
- **Android Adapter**: Placeholder para futura integración con Firebase Cloud Messaging (FCM)
- **iOS Adapter**: Placeholder para futura integración con Apple Push Notification Service (APNs)

## Características

- ✅ Envío de notificaciones individuales y en lote
- ✅ Soporte para WebPush con claves VAPID
- ✅ Placeholders para Android e iOS
- ✅ Seguimiento de estado de notificaciones
- ✅ Estadísticas de envío por canal
- ✅ Integración con el CRM para campañas

## Configuración

### Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tfg_db

# WebPush VAPID
VAPID_PRIVATE_KEY=your_vapid_private_key_here
VAPID_PUBLIC_KEY=your_vapid_public_key_here
VAPID_EMAIL=noreply@mercat.com

# Servicio
LOG_LEVEL=INFO
```

### Generar Claves VAPID

Para WebPush, necesitas generar claves VAPID:

```bash
cd modules/backend/notification-sender
python generate_vapid_keys.py
```

## Endpoints

### Envío de Notificaciones

- `POST /send` - Enviar notificación individual
- `POST /send-batch` - Enviar múltiples notificaciones
- `GET /status/{notification_id}` - Obtener estado de notificación
- `GET /stats` - Estadísticas del servicio

### Ejemplo de Uso

```bash
# Enviar notificación individual
curl -X POST "http://localhost:8007/send" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "message": "¡Nueva oferta disponible!",
    "title": "Oferta Especial",
    "channel": "webpush",
    "data": {"url": "/offers/123"}
  }'

# Enviar notificaciones en lote
curl -X POST "http://localhost:8007/send-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "message": "Notificación 1",
        "title": "Título 1",
        "channel": "webpush"
      },
      {
        "user_id": "456e7890-e89b-12d3-a456-426614174001",
        "message": "Notificación 2",
        "title": "Título 2",
        "channel": "webpush"
      }
    ]
  }'
```

## Integración con CRM

El CRM puede enviar notificaciones de campañas usando:

```bash
# Enviar notificaciones de una campaña
curl -X POST "http://localhost:8006/campaigns/{campaign_id}/send-notifications?channel=webpush" \
  -H "Authorization: Bearer {token}"
```

## Estructura de Datos

### UserSubscription

```sql
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL, -- webpush, android, ios
    subscription_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Notification

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    campaign_id UUID,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'queued', -- queued, sent, failed
    meta JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Desarrollo

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar en Desarrollo

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8007
```

### Ejecutar con Docker

```bash
docker build -t notification-sender .
docker run -p 8007:8007 notification-sender
```

## Próximos Pasos

1. **Implementar Android Adapter**: Integrar con Firebase Cloud Messaging
2. **Implementar iOS Adapter**: Integrar con Apple Push Notification Service
3. **Añadir retry logic**: Reintentos automáticos para notificaciones fallidas
4. **Métricas avanzadas**: Dashboard de métricas de envío
5. **Rate limiting**: Limitar envíos por usuario/canal
6. **Templates**: Plantillas de notificaciones reutilizables

## Troubleshooting

### WebPush no funciona

1. Verificar que las claves VAPID estén configuradas
2. Comprobar que el endpoint de suscripción sea válido
3. Revisar logs del servicio

### Notificaciones no se envían

1. Verificar que el usuario tenga suscripción activa
2. Comprobar estado de la base de datos
3. Revisar logs del adapter correspondiente


