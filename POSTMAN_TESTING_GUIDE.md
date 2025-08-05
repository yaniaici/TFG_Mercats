# 🧪 Guía de Pruebas con Postman

## 🚀 Servicios Disponibles

| Servicio | URL | Puerto | Estado |
|----------|-----|--------|--------|
| **Auth Service** | http://localhost:8001 | 8001 | ✅ Activo |
| **Main Backend** | http://localhost:8000 | 8000 | ✅ Activo |
| **PostgreSQL** | localhost | 5432 | ✅ Activo |
| **PgAdmin** | http://localhost:8080 | 8080 | ✅ Activo |

## 📋 Configuración de Postman

### 1. **Variables de Entorno**
Crea un entorno en Postman con estas variables:
```
BASE_URL_AUTH=http://localhost:8001
BASE_URL_BACKEND=http://localhost:8000
TOKEN={{auth_token}}
USER_ID={{user_id}}
```

### 2. **Headers Comunes**
```
Content-Type: application/json
Authorization: Bearer {{TOKEN}}
```

---

## 🔐 AUTH SERVICE (Puerto 8001)

### **1. Health Check**
```
GET {{BASE_URL_AUTH}}/health
```
**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### **2. Información del Servicio**
```
GET {{BASE_URL_AUTH}}/
```
**Respuesta esperada:**
```json
{
  "message": "Servicio de Autenticación",
  "version": "1.0.0",
  "endpoints": {
    "register": "/auth/register",
    "login": "/auth/login",
    "verify": "/auth/verify",
    "refresh": "/auth/refresh",
    "users": "/users"
  }
}
```

### **3. Registrar Usuario**
```
POST {{BASE_URL_AUTH}}/auth/register
Content-Type: application/json

{
  "email_hash": "test@example.com",
  "password": "test123",
  "preferences": {
    "theme": "dark",
    "language": "es"
  }
}
```
**Respuesta esperada (201):**
```json
{
  "id": "uuid-del-usuario",
  "email_hash": "test@example.com",
  "preferences": {
    "theme": "dark",
    "language": "es"
  },
  "registration_date": "2024-01-01T12:00:00",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### **4. Login de Usuario**
```
POST {{BASE_URL_AUTH}}/auth/login
Content-Type: application/json

{
  "email_hash": "test@example.com",
  "password": "test123"
}
```
**Respuesta esperada (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "uuid-del-usuario",
  "expires_in": 1800
}
```
**⚠️ IMPORTANTE:** Guarda el `access_token` en la variable `{{TOKEN}}` y el `user_id` en `{{USER_ID}}`

### **5. Verificar Token**
```
POST {{BASE_URL_AUTH}}/auth/verify
Content-Type: application/json

{
  "token": "{{TOKEN}}"
}
```
**Respuesta esperada (200):**
```json
{
  "valid": true,
  "user_id": "uuid-del-usuario"
}
```

### **6. Obtener Usuario Actual**
```
GET {{BASE_URL_AUTH}}/users/me
Authorization: Bearer {{TOKEN}}
```
**Respuesta esperada (200):**
```json
{
  "id": "uuid-del-usuario",
  "email_hash": "test@example.com",
  "preferences": {
    "theme": "dark",
    "language": "es"
  },
  "registration_date": "2024-01-01T12:00:00",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### **7. Actualizar Usuario**
```
PUT {{BASE_URL_AUTH}}/users/me
Authorization: Bearer {{TOKEN}}
Content-Type: application/json

{
  "preferences": {
    "theme": "light",
    "language": "en",
    "notifications": true
  }
}
```

---

## 🚀 MAIN BACKEND (Puerto 8000)

### **1. Health Check**
```
GET {{BASE_URL_BACKEND}}/health
```
**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### **2. Información del Servicio**
```
GET {{BASE_URL_BACKEND}}/
```
**Respuesta esperada:**
```json
{
  "message": "Sistema de Análisis de Tickets - Backend",
  "version": "1.0.0",
  "endpoints": {
    "tickets": "/tickets",
    "profiles": "/users/{user_id}/profile",
    "gamification": "/gamification",
    "analytics": "/analytics"
  },
  "note": "Autenticación manejada por auth-service en puerto 8001"
}
```

### **3. Debug - Conexión a BD**
```
GET {{BASE_URL_BACKEND}}/debug/db
```
**Respuesta esperada:**
```json
{
  "status": "DB connected",
  "message": "Conexión exitosa a PostgreSQL"
}
```

### **4. Debug - Configuración**
```
GET {{BASE_URL_BACKEND}}/debug/config
```
**Respuesta esperada:**
```json
{
  "database_url": "postgresql://***@localhost:5432/ticket_analytics",
  "debug": false,
  "log_level": "INFO",
  "host": "0.0.0.0",
  "port": 8000
}
```

---

## 🎫 TICKET SERVICE (Puerto 8003)

### **Variables de Entorno Postman**
```
BASE_URL_TICKET = http://localhost:8003
```

### **1. Health Check**
```
GET {{BASE_URL_TICKET}}/health
```
**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### **2. Información del Servicio**
```
GET {{BASE_URL_TICKET}}/
```
**Respuesta esperada:**
```json
{
  "message": "Servicio de Tickets",
  "version": "1.0.0",
  "endpoints": {
    "upload_ticket": "/tickets/upload",
    "get_tickets": "/tickets",
    "get_ticket": "/tickets/{ticket_id}",
    "update_ticket": "/tickets/{ticket_id}",
    "delete_ticket": "/tickets/{ticket_id}"
  }
}
```

### **3. Subir Ticket (Imagen)**
```
POST {{BASE_URL_TICKET}}/tickets/upload
Authorization: Bearer {{TOKEN}}
Content-Type: multipart/form-data

// En la pestaña "Body" -> "form-data":
// Key: file (Type: File)
// Value: Seleccionar archivo de imagen (JPG, JPEG, PNG)
```
**Respuesta esperada (201):**
```json
{
  "message": "Ticket subido exitosamente",
  "ticket": {
    "id": "uuid-del-ticket",
    "user_id": "uuid-del-usuario",
    "filename": "unique_filename.jpg",
    "original_filename": "ticket.jpg",
    "file_path": "/app/uploads/user_id/filename.jpg",
    "file_size": 1024,
    "mime_type": "image/jpeg",
    "status": "pending",
    "metadata": {},
    "processing_result": {},
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
}
```

### **4. Obtener Tickets del Usuario**
```
GET {{BASE_URL_TICKET}}/tickets
Authorization: Bearer {{TOKEN}}
```
**Parámetros opcionales:**
- `skip`: Número de registros a omitir (paginación)
- `limit`: Número máximo de registros (máximo 100)

**Respuesta esperada (200):**
```json
[
  {
    "id": "uuid-del-ticket",
    "user_id": "uuid-del-usuario",
    "filename": "unique_filename.jpg",
    "original_filename": "ticket.jpg",
    "file_path": "/app/uploads/user_id/filename.jpg",
    "file_size": 1024,
    "mime_type": "image/jpeg",
    "status": "pending",
    "metadata": {},
    "processing_result": {},
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

### **5. Obtener Ticket Específico**
```
GET {{BASE_URL_TICKET}}/tickets/{{TICKET_ID}}
Authorization: Bearer {{TOKEN}}
```
**Respuesta esperada (200):**
```json
{
  "id": "uuid-del-ticket",
  "user_id": "uuid-del-usuario",
  "filename": "unique_filename.jpg",
  "original_filename": "ticket.jpg",
  "file_path": "/app/uploads/user_id/filename.jpg",
  "file_size": 1024,
  "mime_type": "image/jpeg",
  "status": "pending",
  "metadata": {},
  "processing_result": {},
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### **6. Actualizar Ticket**
```
PUT {{BASE_URL_TICKET}}/tickets/{{TICKET_ID}}
Authorization: Bearer {{TOKEN}}
Content-Type: application/json

{
  "status": "processed",
  "metadata": {
    "store": "Walmart",
    "amount": 25.50
  },
  "processing_result": {
    "total": 25.50,
    "items": 3,
    "currency": "USD"
  }
}
```
**Respuesta esperada (200):**
```json
{
  "id": "uuid-del-ticket",
  "user_id": "uuid-del-usuario",
  "filename": "unique_filename.jpg",
  "original_filename": "ticket.jpg",
  "file_path": "/app/uploads/user_id/filename.jpg",
  "file_size": 1024,
  "mime_type": "image/jpeg",
  "status": "processed",
  "metadata": {
    "store": "Walmart",
    "amount": 25.50
  },
  "processing_result": {
    "total": 25.50,
    "items": 3,
    "currency": "USD"
  },
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### **7. Eliminar Ticket**
```
DELETE {{BASE_URL_TICKET}}/tickets/{{TICKET_ID}}
Authorization: Bearer {{TOKEN}}
```
**Respuesta esperada (200):**
```json
{
  "message": "Ticket eliminado exitosamente"
}
```

### **Notas Importantes para Ticket Service:**

1. **Autenticación**: Todos los endpoints requieren token JWT válido
2. **Formatos de archivo**: Solo JPG, JPEG, PNG
3. **Tamaño máximo**: 10MB por archivo
4. **Almacenamiento**: Los archivos se guardan en directorios por usuario
5. **Estados del ticket**: 
   - `pending`: Recién subido
   - `processed`: Procesado por AI
   - `failed`: Error en procesamiento

### **5. Crear Perfil de Usuario**
```
POST {{BASE_URL_BACKEND}}/users/{{USER_ID}}/profile
Authorization: Bearer {{TOKEN}}
Content-Type: application/json

{
  "user_type": "regular",
  "segment": "alto_gasto"
}
```
**Respuesta esperada (201):**
```json
{
  "id": "uuid-del-perfil",
  "user_id": "uuid-del-usuario",
  "user_type": "regular",
  "segment": "alto_gasto",
  "gamification_points": 0,
  "level": 1,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### **6. Obtener Perfil de Usuario**
```
GET {{BASE_URL_BACKEND}}/users/{{USER_ID}}/profile
Authorization: Bearer {{TOKEN}}
```

### **7. Crear Ticket**
```
POST {{BASE_URL_BACKEND}}/tickets
Authorization: Bearer {{TOKEN}}
Content-Type: application/json

{
  "purchase_datetime": "2024-01-01T12:00:00",
  "store_id": "tienda_123",
  "total_price": 25.50,
  "origin": "digital",
  "ticket_hash": "hash_del_ticket_123"
}
```
**Respuesta esperada (201):**
```json
{
  "id": "uuid-del-ticket",
  "user_id": "uuid-del-usuario",
  "purchase_datetime": "2024-01-01T12:00:00",
  "store_id": "tienda_123",
  "total_price": 25.50,
  "origin": "digital",
  "ticket_hash": "hash_del_ticket_123",
  "processed": false,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### **8. Obtener Tickets del Usuario**
```
GET {{BASE_URL_BACKEND}}/tickets
Authorization: Bearer {{TOKEN}}
```

### **9. Obtener Ticket Específico**
```
GET {{BASE_URL_BACKEND}}/tickets/{{ticket_id}}
Authorization: Bearer {{TOKEN}}
```

### **10. Perfil de Gamificación**
```
GET {{BASE_URL_BACKEND}}/gamification/profile
Authorization: Bearer {{TOKEN}}
```
**Respuesta esperada:**
```json
{
  "user_id": "uuid-del-usuario",
  "points": 0,
  "level": 1,
  "user_type": "regular",
  "segment": "alto_gasto"
}
```

### **11. Añadir Puntos de Gamificación**
```
POST {{BASE_URL_BACKEND}}/gamification/add-points?points=50
Authorization: Bearer {{TOKEN}}
```
**Respuesta esperada:**
```json
{
  "message": "Puntos añadidos: 50",
  "new_total": 50,
  "new_level": 1
}
```

### **12. Estadísticas del Usuario**
```
GET {{BASE_URL_BACKEND}}/analytics/user-stats
Authorization: Bearer {{TOKEN}}
```
**Respuesta esperada:**
```json
{
  "total_tickets": 1,
  "processed_tickets": 0,
  "total_spent": 25.50,
  "processing_rate": 0.0,
  "gamification_points": 50,
  "level": 1
}
```

### **13. Tabla de Líderes**
```
GET {{BASE_URL_BACKEND}}/analytics/leaderboard?limit=10
Authorization: Bearer {{TOKEN}}
```
**Respuesta esperada:**
```json
[
  {
    "user_id": "uuid-del-usuario",
    "points": 50,
    "level": 1,
    "user_type": "regular"
  }
]
```

---

## 🗄️ PgAdmin (Puerto 8080)

### **Acceso a PgAdmin**
- **URL:** http://localhost:8080
- **Usuario:** admin@admin.com
- **Contraseña:** admin

### **Configurar Conexión a PostgreSQL**
1. Click en "Add New Server"
2. **General Tab:**
   - Name: `TFG Database`
3. **Connection Tab:**
   - Host: `postgres`
   - Port: `5432`
   - Database: `ticket_analytics`
   - Username: `ticket_user`
   - Password: `ticket_password`

---

## 🧪 Flujo de Pruebas Recomendado

### **1. Verificar Servicios**
```bash
# Health checks
GET http://localhost:8001/health  # Auth Service
GET http://localhost:8000/health  # Main Backend
```

### **2. Autenticación**
```bash
# 1. Registrar usuario
POST http://localhost:8001/auth/register

# 2. Hacer login
POST http://localhost:8001/auth/login

# 3. Verificar token
POST http://localhost:8001/auth/verify
```

### **3. Crear Datos**
```bash
# 1. Crear perfil
POST http://localhost:8000/users/{user_id}/profile

# 2. Crear ticket
POST http://localhost:8000/tickets

# 3. Añadir puntos
POST http://localhost:8000/gamification/add-points?points=100
```

### **4. Consultar Datos**
```bash
# 1. Ver perfil
GET http://localhost:8000/gamification/profile

# 2. Ver estadísticas
GET http://localhost:8000/analytics/user-stats

# 3. Ver tickets
GET http://localhost:8000/tickets
```

---

## ⚠️ Errores Comunes

### **401 Unauthorized**
- **Causa:** Token no válido o expirado
- **Solución:** Hacer login nuevamente

### **404 Not Found**
- **Causa:** Endpoint incorrecto o ID no válido
- **Solución:** Verificar URL y parámetros

### **422 Validation Error**
- **Causa:** Datos de entrada incorrectos
- **Solución:** Verificar formato JSON y campos requeridos

### **500 Internal Server Error**
- **Causa:** Error en el servidor
- **Solución:** Revisar logs de Docker

---

## 📊 Verificar en Base de Datos

### **Conectar a PostgreSQL**
```bash
docker exec -it tfg_postgres psql -U ticket_user -d ticket_analytics
```

### **Consultas Útiles**
```sql
-- Ver tablas
\dt

-- Ver usuarios
SELECT * FROM users;

-- Ver perfiles
SELECT * FROM user_profiles;

-- Ver tickets
SELECT * FROM tickets;

-- Ver logs de auditoría
SELECT * FROM audit_logs;
```

---

## 🎯 Próximos Pasos

1. **Probar todos los endpoints** en el orden recomendado
2. **Verificar datos** en PgAdmin
3. **Probar casos de error** (tokens inválidos, datos incorrectos)
4. **Crear múltiples usuarios** para probar leaderboard
5. **Probar con diferentes tipos de tickets**

¡Disfruta probando el sistema! 🚀 