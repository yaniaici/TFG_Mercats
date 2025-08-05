# AI Ticket Processor - Gemini API

Servicio de procesamiento de tickets de compra utilizando la API de Google Gemini 2.0 Flash para extracción inteligente de información.

## 🚀 Características

- **Procesamiento con IA**: Utiliza Gemini 2.0 Flash para análisis inteligente de imágenes
- **Extracción estructurada**: Obtiene fecha, hora, tienda, total y productos en formato JSON
- **Clasificación automática**: Identifica el tipo de ticket (supermercado, restaurante, etc.)
- **API REST**: Endpoints para procesamiento individual y en lote
- **Logging estructurado**: Registro detallado de operaciones

## 📋 Requisitos

- Python 3.8+
- API Key de Google Gemini
- Docker (opcional)

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `env.example`:

```bash
# API Key de Gemini (obligatoria)
GEMINI_API_KEY=your_gemini_api_key_here

# Configuración del servicio
PORT=8003
LOG_LEVEL=INFO
```

### Instalación Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servicio
python main.py
```

### Docker

#### Usando Scripts (Recomendado)

**Linux/Mac:**
```bash
# Dar permisos de ejecución
chmod +x docker-run.sh

# Construir y ejecutar
./docker-run.sh build
./docker-run.sh run

# Probar el servicio
./docker-run.sh test

# Ver logs
./docker-run.sh logs
```

**Windows (PowerShell):**
```powershell
# Construir y ejecutar
.\docker-run.ps1 build
.\docker-run.ps1 run

# Probar el servicio
.\docker-run.ps1 test

# Ver logs
.\docker-run.ps1 logs
```

#### Usando Docker Compose

```bash
# Desde el directorio raíz del proyecto
docker-compose up -d ai-ticket-processor

# Ver logs
docker-compose logs -f ai-ticket-processor

# Detener
docker-compose down ai-ticket-processor
```

#### Comandos Docker Manuales

```bash
# Construir imagen
docker build -t ai-ticket-processor .

# Ejecutar contenedor
docker run -d --name ai-ticket-processor \
  --env-file .env \
  -p 8003:8003 \
  -v $(pwd)/images:/app/images:ro \
  ai-ticket-processor

# Ver logs
docker logs -f ai-ticket-processor

# Detener y eliminar
docker stop ai-ticket-processor && docker rm ai-ticket-processor
```

## 🎯 Uso

### Endpoint Principal

```bash
POST /process-ticket
```

**Parámetros:**
- `file`: Archivo de imagen (jpg, jpeg, png)

**Respuesta:**
```json
{
    "fecha": "06/09/2024",
    "hora": "19:24",
    "tienda": "MERCADONA",
    "total": "45.67",
    "tipo_ticket": "supermercado",
    "productos": [
        {
            "cantidad": "2",
            "nombre": "Leche entera",
            "precio": "1.20"
        }
    ],
    "num_productos": 1,
    "procesado_correctamente": true,
    "metodo": "Gemini 2.0 Flash API"
}
```

### Procesamiento en Lote

```bash
POST /process-ticket-batch
```

**Parámetros:**
- `files`: Lista de archivos de imagen

### Información del Modelo

```bash
GET /model-info
```

## 🧪 Testing

```bash
# Probar con imagen de ejemplo
python test_ticket.py

# Probar endpoints
pytest
```

## 📊 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información del servicio |
| `/health` | GET | Estado de salud |
| `/process-ticket` | POST | Procesar un ticket |
| `/process-ticket-batch` | POST | Procesar múltiples tickets |
| `/model-info` | GET | Información del modelo |

## 🔍 Logs

El servicio utiliza logging estructurado con `structlog`. Los logs incluyen:

- Inicialización del sistema
- Procesamiento de tickets
- Errores de API
- Métricas de rendimiento

## 🛠️ Desarrollo

### Estructura del Código

```
ai-ticket-processor/
├── main.py              # Servidor FastAPI
├── ai_system.py         # Lógica de procesamiento con Gemini
├── test_ticket.py       # Script de pruebas
├── requirements.txt     # Dependencias
└── README.md           # Documentación
```

### Flujo de Procesamiento

1. **Recepción**: El servicio recibe una imagen de ticket
2. **Codificación**: La imagen se convierte a base64
3. **API Call**: Se envía a Gemini con un prompt específico
4. **Parsing**: Se extrae y valida el JSON de respuesta
5. **Respuesta**: Se devuelve la información estructurada

## 🔒 Seguridad

- Validación de tipos de archivo
- Límites de tamaño de imagen
- Manejo seguro de errores
- Logging sin información sensible

## 📈 Monitoreo

- Endpoint de salud (`/health`)
- Logs estructurados
- Métricas de procesamiento
- Manejo de errores detallado

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. 