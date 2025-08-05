# 🐳 Docker Compose - TFG Sistema de Mercado

Este archivo `docker-compose.yml` proporciona la configuración para ejecutar el servicio de procesamiento de tickets con IA del TFG Sistema de Mercado.

## 📋 Servicios Incluidos

### 🔧 Servicios Backend
- **ai-ticket-processor** (puerto 8003) - Procesamiento de tickets con IA

## 🚀 Comandos de Uso

### Inicio Rápido
```bash
# Ejecutar el servicio
docker-compose up -d

# Ejecutar en modo desarrollo (ver logs)
docker-compose up
```

### Gestión del Servicio
```bash
# Ver logs del servicio
docker-compose logs -f ai-ticket-processor

# Reiniciar el servicio
docker-compose restart ai-ticket-processor

# Parar el servicio
docker-compose down

# Ver estado del servicio
docker-compose ps
```

### Construcción de Imágenes
```bash
# Construir la imagen
docker-compose build

# Reconstruir sin cache
docker-compose build --no-cache
```

## ⚙️ Configuración

### Variables de Entorno
El servicio utiliza las siguientes variables de entorno (opcionales):
- `LOG_LEVEL` - Nivel de logging (default: INFO)
- `DEBUG` - Modo debug (default: false)
- `ENVIRONMENT` - Entorno de ejecución (default: production)

### Puertos Utilizados
- **8003**: AI Ticket Processor

## 📁 Volúmenes

El servicio monta el directorio de imágenes local:
- `./modules/backend/ai-ticket-processor/images:/app/images`

## 🌐 Redes

El servicio está conectado a la red `tfg_network`.

## 🔧 Desarrollo

### Agregar Nuevos Servicios
Cuando crees nuevos servicios con Dockerfile, puedes agregarlos al docker-compose.yml siguiendo este patrón:

```yaml
nuevo-servicio:
  build:
    context: ./modules/backend/nuevo-servicio
    dockerfile: Dockerfile
  container_name: tfg_nuevo_servicio
  restart: unless-stopped
  environment:
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
  ports:
    - "8004:8004"
  networks:
    - tfg_network
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Puerto ya en uso**
   ```bash
   # Verificar qué proceso usa el puerto
   netstat -ano | findstr :8003
   # Cambiar el puerto en docker-compose.yml
   ```

2. **Servicio no inicia**
   ```bash
   # Ver logs del servicio
   docker-compose logs ai-ticket-processor
   # Verificar configuración
   docker-compose config
   ```

### Limpieza
```bash
# Eliminar contenedores y redes
docker-compose down

# Eliminar imágenes no utilizadas
docker image prune -a

# Limpiar todo el sistema Docker
docker system prune -a
```

## 📚 Recursos Adicionales

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Python Docker](https://hub.docker.com/_/python) 