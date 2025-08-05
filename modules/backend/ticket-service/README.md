# Ticket Service

Servicio para la gestión de tickets de usuarios. Permite a los usuarios autenticados subir imágenes de tickets que posteriormente serán procesadas por el AI Ticket Processor.

## Características

- ✅ Subida de imágenes de tickets (JPG, JPEG, PNG)
- ✅ Autenticación mediante JWT tokens
- ✅ Validación de archivos (tamaño y extensión)
- ✅ Gestión de tickets por usuario
- ✅ Almacenamiento seguro de archivos
- ✅ API RESTful completa

## Estructura del Proyecto

```
ticket-service/
├── main.py              # Aplicación principal FastAPI
├── models.py            # Modelos de base de datos
├── schemas.py           # Esquemas Pydantic
├── database.py          # Configuración de base de datos
├── config.py            # Configuración del servicio
├── auth_client.py       # Cliente de autenticación
├── utils.py             # Utilidades para manejo de archivos
├── requirements.txt     # Dependencias de Python
├── Dockerfile           # Configuración de Docker
├── env.example          # Variables de entorno de ejemplo
└── README.md           # Este archivo
```

## Instalación

### Requisitos

- Python 3.11+
- PostgreSQL
- Auth Service ejecutándose

### Instalación Local

1. Clonar el repositorio
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno:
   ```bash
   cp env.example .env
   # Editar .env con tus configuraciones
   ```

4. Ejecutar el servicio:
   ```bash
   python main.py
   ```

### Docker

```bash
docker build -t ticket-service .
docker run -p 8003:8003 ticket-service
```

## Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://ticket_user:ticket_password@localhost:5432/ticket_analytics` |
| `HOST` | Host del servidor | `0.0.0.0` |
| `PORT` | Puerto del servidor | `8003` |
| `UPLOAD_DIR` | Directorio de almacenamiento | `./uploads` |
| `MAX_FILE_SIZE` | Tamaño máximo de archivo (bytes) | `10485760` (10MB) |
| `AUTH_SERVICE_URL` | URL del servicio de autenticación | `http://localhost:8001` |
| `DEBUG` | Modo debug | `false` |

## API Endpoints

### Autenticación

Todos los endpoints requieren autenticación mediante JWT token en el header:
```
Authorization: Bearer <token>
```

### Endpoints Disponibles

#### `POST /tickets/upload`
Subir un nuevo ticket (imagen)

**Parámetros:**
- `file`: Archivo de imagen (JPG, JPEG, PNG)

**Respuesta:**
```json
{
  "message": "Ticket subido exitosamente",
  "ticket": {
    "id": "uuid",
    "user_id": "uuid",
    "filename": "unique_filename.jpg",
    "original_filename": "ticket.jpg",
    "file_path": "/path/to/file",
    "file_size": 1024,
    "mime_type": "image/jpeg",
    "status": "pending",
    "metadata": {},
    "processing_result": {},
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### `GET /tickets`
Obtener todos los tickets del usuario actual

**Parámetros de consulta:**
- `skip`: Número de registros a omitir (paginación)
- `limit`: Número máximo de registros a retornar

#### `GET /tickets/{ticket_id}`
Obtener un ticket específico

#### `PUT /tickets/{ticket_id}`
Actualizar un ticket específico

**Body:**
```json
{
  "status": "processed",
  "metadata": {"store": "Walmart"},
  "processing_result": {"total": 25.50}
}
```

#### `DELETE /tickets/{ticket_id}`
Eliminar un ticket específico

## Modelo de Datos

### Ticket

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `user_id` | UUID | ID del usuario propietario |
| `filename` | String | Nombre único del archivo |
| `original_filename` | String | Nombre original del archivo |
| `file_path` | String | Ruta del archivo en el sistema |
| `file_size` | Integer | Tamaño del archivo en bytes |
| `mime_type` | String | Tipo MIME del archivo |
| `status` | String | Estado del ticket (pending, processed, failed) |
| `metadata` | JSONB | Metadatos adicionales |
| `processing_result` | JSONB | Resultado del procesamiento AI |
| `created_at` | DateTime | Fecha de creación |
| `updated_at` | DateTime | Fecha de última actualización |

## Seguridad

- **Autenticación**: JWT tokens verificados con el auth-service
- **Autorización**: Usuarios solo pueden acceder a sus propios tickets
- **Validación de archivos**: Verificación de extensión y tamaño
- **Almacenamiento seguro**: Archivos guardados con nombres únicos
- **CORS**: Configurado para permitir acceso desde frontend

## Integración con AI Ticket Processor

Los tickets subidos tienen estado inicial "pending" y pueden ser actualizados por el AI Ticket Processor con:
- Estado: "processed" o "failed"
- Resultado del procesamiento en `processing_result`

## Desarrollo

### Ejecutar en modo desarrollo

```bash
export DEBUG=true
python main.py
```

### Ejecutar tests

```bash
# TODO: Implementar tests
```

## Troubleshooting

### Error de conexión a base de datos
- Verificar que PostgreSQL esté ejecutándose
- Verificar la URL de conexión en `DATABASE_URL`

### Error de autenticación
- Verificar que el auth-service esté ejecutándose
- Verificar la URL en `AUTH_SERVICE_URL`

### Error al subir archivos
- Verificar permisos en el directorio `UPLOAD_DIR`
- Verificar que el archivo no exceda `MAX_FILE_SIZE`
- Verificar que la extensión esté en `ALLOWED_EXTENSIONS` 