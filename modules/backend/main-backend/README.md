# Backend del Sistema de Análisis de Tickets

Este es el backend completo del sistema de análisis de tickets, desarrollado con FastAPI. Incluye todas las funcionalidades necesarias para gestionar usuarios, tickets, gamificación y analíticas.

## Características

- **Autenticación**: Sistema completo de registro e inicio de sesión con JWT
- **Gestión de usuarios**: CRUD completo para usuarios y perfiles
- **Gestión de tickets**: Creación, lectura y actualización de tickets de compra
- **Gamificación**: Sistema de puntos y niveles para fidelización
- **Analíticas**: Estadísticas de usuario y tabla de líderes
- **Seguridad**: Contraseñas hasheadas con bcrypt y autenticación JWT
- **Base de datos**: PostgreSQL con SQLAlchemy ORM

## Endpoints disponibles

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión

### Usuarios
- `GET /users/me` - Obtener información del usuario actual
- `PUT /users/me` - Actualizar información del usuario actual
- `GET /users/{user_id}` - Obtener información de un usuario específico

### Perfiles
- `POST /users/{user_id}/profile` - Crear perfil de usuario
- `GET /users/{user_id}/profile` - Obtener perfil de usuario
- `PUT /users/{user_id}/profile` - Actualizar perfil de usuario

### Tickets
- `POST /tickets` - Crear nuevo ticket
- `GET /tickets` - Obtener tickets del usuario
- `GET /tickets/{ticket_id}` - Obtener ticket específico
- `PUT /tickets/{ticket_id}` - Actualizar ticket

### Gamificación
- `GET /gamification/profile` - Obtener perfil de gamificación
- `POST /gamification/add-points` - Añadir puntos de gamificación

### Analíticas
- `GET /analytics/user-stats` - Obtener estadísticas del usuario
- `GET /analytics/leaderboard` - Obtener tabla de líderes

## Configuración

1. Copiar el archivo de variables de entorno:
```bash
cp env.example .env
```

2. Configurar las variables en `.env`:
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `SECRET_KEY`: Clave secreta para JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración del token
- `GEMINI_API_KEY`: API key para integración con IA (opcional)

## Instalación y ejecución

### Con Docker
```bash
# Desde el directorio raíz del proyecto
docker-compose up backend
```

### Localmente
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Estructura del proyecto

```
backend/
├── main.py              # Aplicación principal FastAPI
├── database.py          # Configuración de base de datos
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Esquemas Pydantic
├── auth.py              # Autenticación JWT
├── requirements.txt     # Dependencias
├── Dockerfile           # Configuración Docker
├── env.example          # Variables de entorno de ejemplo
└── README.md            # Documentación
```

## Modelos de datos

### User
- `id`: UUID único
- `email_hash`: Hash del email (privacidad)
- `password_hash`: Hash de la contraseña
- `preferences`: Preferencias en formato JSON
- `is_active`: Estado del usuario

### UserProfile
- `user_id`: Referencia al usuario
- `user_type`: Tipo (regular, turista, ciudadano)
- `segment`: Segmento de comportamiento
- `gamification_points`: Puntos de gamificación
- `level`: Nivel actual

### Ticket
- `user_id`: Usuario propietario (opcional)
- `purchase_datetime`: Fecha de compra
- `store_id`: ID de la tienda
- `total_price`: Precio total
- `origin`: Origen (escaneo, digital, API)
- `processed`: Estado de procesamiento por IA

## Ejemplos de uso

### Registrar usuario
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email_hash": "hash_del_email",
       "password": "contraseña123",
       "preferences": {"language": "es", "notifications": true}
     }'
```

### Crear ticket
```bash
curl -X POST "http://localhost:8000/tickets" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
       "purchase_datetime": "2024-01-15T10:30:00Z",
       "store_id": "tienda_123",
       "total_price": 45.50,
       "origin": "escaneo",
       "ticket_hash": "hash_del_ticket"
     }'
```

### Añadir puntos de gamificación
```bash
curl -X POST "http://localhost:8000/gamification/add-points?points=50" \
     -H "Authorization: Bearer {token}"
```

## Integración con otros servicios

### Procesador de IA
El backend puede integrarse con el procesador de IA para:
- Marcar tickets como procesados
- Obtener análisis de tickets
- Actualizar estadísticas

### Base de datos
- PostgreSQL como base de datos principal
- Tablas para usuarios, perfiles, tickets e imágenes
- Logs de auditoría para seguimiento de cambios

## Desarrollo

### Agregar nuevos endpoints
1. Definir el esquema en `schemas.py`
2. Crear el endpoint en `main.py`
3. Actualizar la documentación

### Migraciones de base de datos
```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head
```

## Documentación de la API

Una vez ejecutado el servidor, la documentación automática estará disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Monitoreo y logs

- Health check: `GET /health`
- Logs de aplicación en stdout/stderr
- Logs de auditoría en base de datos 