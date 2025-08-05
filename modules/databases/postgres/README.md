# Base de Datos PostgreSQL - Ticket Analytics

Esta es la base de datos principal del sistema de análisis de tickets, diseñada con enfoque en la privacidad y el rendimiento.

## 🏗️ Arquitectura

### Entidades Principales

#### 1. **Users** (Usuarios)
- **id**: UUID (clave primaria, generada automáticamente)
- **email_hash**: Hash del email (para evitar duplicados sin almacenar el email real)
- **password_hash**: Hash de la contraseña (nunca en texto plano)
- **registration_date**: Fecha de registro
- **preferences**: JSONB con preferencias (notificaciones, idioma, etc.)
- **is_active**: Estado activo/inactivo
- **created_at/updated_at**: Timestamps automáticos

#### 2. **UserProfiles** (Perfiles de Usuario)
- **id**: UUID (clave primaria)
- **user_id**: Relación con Users
- **user_type**: Tipo de usuario (regular, turista, ciudadano)
- **segment**: Clúster o segmento de comportamiento
- **gamification_points**: Puntos de gamificación
- **level**: Nivel de fidelización

#### 3. **Tickets** (Tickets de Compra)
- **id**: UUID (clave primaria)
- **user_id**: Relación con Users (puede ser NULL para anónimos)
- **purchase_datetime**: Fecha y hora de compra
- **store_id**: ID de la tienda
- **total_price**: Precio total
- **origin**: Origen (escaneo, digital, API)
- **ticket_hash**: Hash del ticket para evitar duplicados
- **processed**: Estado de procesamiento por IA

#### 4. **TicketImages** (Imágenes de Tickets)
- **id**: UUID (clave primaria)
- **ticket_id**: Relación con Tickets
- **image_path**: Ruta al archivo de imagen
- **image_hash**: Hash de la imagen
- **processed**: Estado de procesamiento
- **expires_at**: Fecha de expiración (auto-eliminación después de 24h)

#### 5. **AuditLogs** (Logs de Auditoría)
- **id**: UUID (clave primaria)
- **table_name**: Nombre de la tabla
- **record_id**: ID del registro
- **action**: Acción (INSERT, UPDATE, DELETE)
- **old_values/new_values**: Valores anteriores y nuevos (JSONB)
- **user_id**: Usuario que realizó la acción
- **created_at**: Timestamp de la acción

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker Desktop instalado y ejecutándose
- PowerShell (Windows) o Bash (Linux/Mac)

### Iniciar la Base de Datos

```powershell
# Desde la raíz del proyecto
.\modules\databases\postgres\scripts\start-db.ps1
```

### Detener la Base de Datos

```powershell
# Desde la raíz del proyecto
.\modules\databases\postgres\scripts\stop-db.ps1
```

### Resetear la Base de Datos

```powershell
# Desde la raíz del proyecto (elimina todos los datos)
.\modules\databases\postgres\scripts\reset-db.ps1
```

### Iniciar Todo el Proyecto

```powershell
# Desde la raíz del proyecto
docker-compose up -d
```

## 📊 Información de Conexión

### PostgreSQL
- **Host**: localhost
- **Puerto**: 5432
- **Base de datos**: ticket_analytics
- **Usuario**: ticket_user
- **Contraseña**: ticket_password

### PgAdmin (Interfaz Web)
- **URL**: http://localhost:8080
- **Email**: admin@ticketanalytics.com
- **Contraseña**: admin123

## 🔧 Características Técnicas

### Extensiones Instaladas
- `uuid-ossp`: Generación de UUIDs
- `pgcrypto`: Funciones criptográficas
- `jsonb`: Soporte JSON nativo
- `pg_stat_statements`: Estadísticas de consultas

### Índices Optimizados
- Índices en campos de búsqueda frecuente
- Índices compuestos para consultas complejas
- Índices en campos de auditoría

### Triggers Automáticos
- **Actualización de timestamps**: `updated_at` se actualiza automáticamente
- **Auditoría**: Todos los cambios se registran en `audit_logs`
- **Limpieza de imágenes**: Eliminación automática de imágenes expiradas

### Vistas Útiles
- `user_complete_info`: Información completa de usuarios
- `user_ticket_stats`: Estadísticas de tickets por usuario
- `ticket_with_user`: Tickets con información de usuario
- `segment_analysis`: Análisis por segmentos
- `pending_tickets`: Tickets pendientes de procesamiento
- `recent_audit_logs`: Logs de auditoría recientes

## 🔒 Seguridad y Privacidad

### Protección de Datos
- **Emails hasheados**: No se almacenan emails en texto plano
- **Contraseñas hasheadas**: Uso de funciones criptográficas
- **Sin datos personales**: No se almacenan nombres, teléfonos, etc.
- **Anonimización**: Soporte para usuarios anónimos

### Auditoría Completa
- Registro de todas las operaciones CRUD
- Trazabilidad de cambios
- Logs de acceso y modificaciones

## 📈 Rendimiento

### Configuraciones Optimizadas
- **Memoria**: 256MB shared_buffers, 1GB effective_cache_size
- **Conexiones**: Máximo 100 conexiones concurrentes
- **WAL**: Configuración optimizada para escritura
- **Autovacuum**: Limpieza automática de datos obsoletos

### Monitoreo
- Logs detallados de rendimiento
- Estadísticas de consultas
- Health checks automáticos

## 🛠️ Mantenimiento

### Backup
```sql
-- Crear backup
pg_dump -h localhost -U ticket_user -d ticket_analytics > backup.sql

-- Restaurar backup
psql -h localhost -U ticket_user -d ticket_analytics < backup.sql
```

### Limpieza de Logs
```sql
-- Limpiar logs antiguos (más de 30 días)
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '30 days';
```

### Estadísticas de Rendimiento
```sql
-- Ver estadísticas de consultas
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- Ver tamaño de tablas
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY tablename, attname;
```

## 🔍 Troubleshooting

### Problemas Comunes

1. **Puerto 5432 ocupado**
   ```powershell
   # Verificar qué usa el puerto
   netstat -ano | findstr :5432
   ```

2. **Contenedor no inicia**
   ```powershell
   # Ver logs del contenedor
   docker-compose logs postgres
   ```

3. **Problemas de permisos**
   ```powershell
   # Resetear volúmenes
   docker-compose down -v
   docker-compose up -d --build
   ```

### Logs de Diagnóstico
- **PostgreSQL logs**: `./logs/` (montado en el contenedor)
- **Docker logs**: `docker-compose logs postgres`
- **Health check**: `docker-compose ps`

## 📚 Referencias

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker PostgreSQL](https://hub.docker.com/_/postgres)
- [PgAdmin Documentation](https://www.pgadmin.org/docs/) 