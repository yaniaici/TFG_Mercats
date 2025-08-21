# Scripts de Inicialización de la Base de Datos TFG

Este directorio contiene todos los scripts SQL necesarios para inicializar la base de datos del proyecto TFG.

## Orden de Ejecución

Los scripts se ejecutan automáticamente en orden alfabético por Docker:

1. **00_init_database.sql** - Script principal con mensajes de inicio y finalización
2. **01_create_extensions.sql** - Extensiones necesarias (uuid-ossp, pgcrypto, pg_stat_statements)
3. **02_create_main_tables.sql** - Tablas principales del sistema
4. **03_create_auth_tables.sql** - Tablas de autenticación y autorización
5. **04_create_triggers.sql** - Triggers y funciones de auditoría
6. **05_create_views.sql** - Vistas útiles del sistema
7. **06_create_purchase_history.sql** - Tabla de historial de compras
8. **07_create_gamification_tables.sql** - Tablas del sistema de gamificación
9. **08_create_rewards_tables.sql** - Tablas del sistema de recompensas
10. **10_create_crm.sql** - Tablas del sistema CRM
11. **11_create_notification_sender_tables.sql** - Tablas de notificaciones
12. **12_insert_initial_data.sql** - Datos iniciales (roles, permisos, usuario admin)
13. **13_create_additional_tables.sql** - Tablas adicionales para servicios específicos
14. **14_verify_tables.sql** - Verificación de que todas las tablas se crearon correctamente

## Tablas Principales

### Usuarios y Autenticación
- `users` - Usuarios del sistema
- `user_profiles` - Perfiles de usuario con datos de gamificación
- `user_sessions` - Sesiones de usuario
- `password_resets` - Tokens de reset de contraseña
- `email_verifications` - Verificación de email
- `failed_login_attempts` - Intentos fallidos de login
- `user_activity_logs` - Logs de actividad de usuario

### Autorización
- `roles` - Roles del sistema
- `permissions` - Permisos disponibles
- `role_permissions` - Relación roles-permisos
- `user_roles` - Relación usuarios-roles

### Tickets y Archivos
- `tickets` - Tickets del sistema (versión unificada)
- `ticket_images` - Imágenes de tickets
- `ticket_attachments` - Archivos adjuntos a tickets
- `ticket_comments` - Comentarios de tickets
- `ticket_files` - Archivos de tickets (para ticket-service)

### Vendedores y Tiendas
- `vendors` - Vendedores del sistema
- `stores` - Tiendas de vendedores
- `market_stores` - Tiendas del mercado

### Gamificación
- `user_gamification` - Perfil de gamificación de usuario
- `user_badges` - Insignias ganadas por usuarios
- `experience_log` - Historial de experiencia

### Recompensas
- `rewards` - Recompensas disponibles
- `reward_redemptions` - Canjes de recompensas

### CRM y Notificaciones
- `segments` - Segmentos de usuarios
- `campaigns` - Campañas de marketing
- `campaign_segments` - Relación campañas-segmentos
- `notifications` - Notificaciones del sistema
- `user_subscriptions` - Suscripciones a notificaciones

### Auditoría y Historial
- `audit_logs` - Logs de auditoría automática
- `purchase_history` - Historial de compras

## Funciones y Triggers

### Funciones Principales
- `get_current_timestamp()` - Obtener timestamp actual
- `update_updated_at_column()` - Actualizar campo updated_at automáticamente
- `audit_trigger_function()` - Crear logs de auditoría automáticamente
- `cleanup_expired_images()` - Limpiar imágenes expiradas
- `cleanup_inactive_subscriptions()` - Limpiar suscripciones inactivas

### Triggers Automáticos
- Triggers para actualizar `updated_at` en todas las tablas principales
- Triggers de auditoría para tablas críticas (users, user_profiles, tickets, ticket_images)
- Trigger para limpiar imágenes expiradas

## Datos Iniciales

El script `12_insert_initial_data.sql` crea:

### Roles
- `admin` - Administrador del sistema
- `vendor` - Vendedor
- `user` - Usuario regular
- `support` - Soporte técnico

### Permisos
- Permisos CRUD para todas las entidades principales
- Permisos específicos para gamificación, recompensas, CRM y notificaciones

### Usuario Administrador
- Usuario: `admin@tfg.com`
- Contraseña: `admin123`
- **IMPORTANTE**: Cambiar la contraseña en producción

## Correcciones Realizadas

### Problemas Solucionados
1. **Tablas faltantes**: Se añadieron `user_profiles`, `audit_logs`, `ticket_images`
2. **Inconsistencias en tickets**: Se unificó la estructura de la tabla `tickets`
3. **Campos faltantes**: Se añadieron campos necesarios como `email_hash`, `registration_date`, `preferences`, `role`
4. **Funciones duplicadas**: Se eliminaron duplicaciones de `update_updated_at_column()`
5. **Orden de ejecución**: Se reorganizaron los scripts para evitar dependencias
6. **Scripts obsoletos**: Se eliminó `09_add_email_field.sql` (campos ya incluidos)

### Mejoras Implementadas
- Mejor documentación y comentarios
- Script de verificación automática
- Índices optimizados para rendimiento
- Triggers de auditoría mejorados
- Estructura más consistente entre servicios

## Verificación

El script `14_verify_tables.sql` verifica automáticamente:
- Que todas las tablas se han creado correctamente
- Que las extensiones necesarias están instaladas
- Que las funciones principales están disponibles

## Notas Importantes

1. **Orden de ejecución**: Los scripts se ejecutan en orden alfabético, por eso se numeran con prefijos
2. **Dependencias**: Algunos scripts dependen de otros, el orden es crítico
3. **Producción**: Cambiar siempre la contraseña del administrador en producción
4. **Backup**: Hacer backup antes de ejecutar en producción
5. **Logs**: Revisar los logs de PostgreSQL para detectar errores durante la inicialización
