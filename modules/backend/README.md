# Backend del Sistema de Análisis de Tickets

Este directorio contiene todos los servicios backend del sistema de análisis de tickets, organizados en módulos específicos.

## Estructura de Servicios

### 🚀 main-backend/
El backend principal que contiene toda la lógica de negocio del sistema:
- **Autenticación** con JWT
- **Gestión de usuarios** y perfiles
- **Gestión de tickets** de compra
- **Sistema de gamificación** con puntos y niveles
- **Analíticas** y estadísticas
- **Integración con base de datos** PostgreSQL

**Documentación**: [Ver README de main-backend](./main-backend/README.md)

### 🤖 ai-ticket-processor/
Servicio de procesamiento de tickets con IA:
- Análisis de imágenes de tickets
- Extracción de datos con Gemini AI
- Procesamiento automático de compras

### 🔐 auth-service/
Servicio dedicado de autenticación (futuro):
- Gestión de tokens
- OAuth/SSO
- Autorización granular

### 📊 analytics/
Servicio de analíticas avanzadas (futuro):
- Dashboards en tiempo real
- Reportes personalizados
- Métricas de negocio

### 🎮 gamification/
Servicio de gamificación avanzada (futuro):
- Sistema de logros
- Badges y recompensas
- Competencias entre usuarios

### 📧 notifications/
Servicio de notificaciones (futuro):
- Notificaciones push
- Emails automáticos
- Alertas personalizadas

### 🎯 recommendations/
Servicio de recomendaciones (futuro):
- Recomendaciones de productos
- Ofertas personalizadas
- Sugerencias de tiendas

### 👥 user-profiling/
Servicio de perfilado de usuarios (futuro):
- Segmentación avanzada
- Análisis de comportamiento
- Predicciones de compra

### 🎫 ticket-service/
Servicio dedicado de tickets (futuro):
- Gestión avanzada de tickets
- Integración con APIs externas
- Validación de tickets

### 🌐 api-gateway/
API Gateway (futuro):
- Enrutamiento de requests
- Rate limiting
- Autenticación centralizada

### 💼 crm/
Servicio de CRM (futuro):
- Gestión de clientes
- Historial de interacciones
- Segmentación de clientes

## Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Mobile App    │    │   Third Party   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      API Gateway          │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │     main-backend          │
                    │  (FastAPI Application)    │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────┴─────────┐  ┌─────────┴─────────┐  ┌─────────┴─────────┐
│  PostgreSQL DB    │  │  Redis Cache      │  │  File Storage     │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

## Estado Actual

### ✅ Completado
- **main-backend**: Backend principal funcional (tickets, gamificación, analytics)
- **auth-service**: Servicio de autenticación funcional
- **ai-ticket-processor**: Procesador de IA funcional
- **Base de datos**: PostgreSQL configurado

### 🚧 En Desarrollo
- Integración entre servicios
- Optimizaciones de rendimiento
- Documentación completa

### 📋 Pendiente
- Servicios adicionales (auth-service, analytics, etc.)
- API Gateway
- Microservicios desacoplados
- Monitoreo y logging avanzado

## Ejecución

### Ejecutar todo el sistema
```bash
# Desde el directorio raíz del proyecto
docker-compose up
```

### Ejecutar solo el backend principal
```bash
docker-compose up backend
```

### Ejecutar solo el servicio de autenticación
```bash
docker-compose up auth-service
```

### Ejecutar solo el procesador de IA
```bash
docker-compose up ai-ticket-processor
```

## Desarrollo

### Agregar un nuevo servicio
1. Crear una nueva carpeta en `modules/backend/`
2. Implementar el servicio con su Dockerfile
3. Agregar el servicio al `docker-compose.yml`
4. Documentar en este README

### Estructura recomendada para nuevos servicios
```
servicio-nombre/
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias
├── Dockerfile           # Configuración Docker
├── env.example          # Variables de entorno
├── README.md            # Documentación
└── tests/               # Pruebas
```

## Documentación

- **main-backend**: [Ver documentación](./main-backend/README.md)
- **auth-service**: [Ver documentación](./auth-service/README.md)
- **ai-ticket-processor**: [Ver documentación](./ai-ticket-processor/README.md)
- **API Documentation**: 
  - Main Backend: http://localhost:8000/docs
  - Auth Service: http://localhost:8001/docs 