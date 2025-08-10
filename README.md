# 🏪 Mercat Mediterrani - Sistema de Tickets y Gamificación

Sistema completo de gestión de tickets para mercados locales con gamificación, CRM y IA integrada.

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

```powershell
# Ejecutar el script de configuración
.\setup-env.ps1
```

Esto creará un archivo `.env` con todas las variables necesarias. **IMPORTANTE**: Revisa y modifica las credenciales sensibles antes de usar en producción.

### 2. Levantar el Sistema

```powershell
# Iniciar todos los servicios
docker compose up -d

# O usar el script de inicio
.\start_system.ps1
```

### 3. Acceder a los Servicios

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **pgAdmin**: http://localhost:8080 (admin@ticketanalytics.com / admin123)

## 🏗️ Arquitectura

### Servicios Backend
- **auth-service** (8001): Autenticación y autorización
- **ticket-service** (8003): Gestión de tickets y compras
- **ai-ticket-processor** (8004): Procesamiento de tickets con IA
- **gamification-service** (8005): Sistema de gamificación y recompensas
- **crm-service** (8006): CRM con segmentación y campañas por IA
- **main-backend** (8000): API principal y orquestación

### Base de Datos
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y sesiones

### IA
- **Ollama**: Modelos de IA locales (Qwen2.5 0.5B)

## 🔧 Configuración

### Variables de Entorno Importantes

```bash
# API Keys
GEMINI_API_KEY=tu_api_key_de_google_gemini

# Secrets
SECRET_KEY=clave_secreta_para_jwt
POSTGRES_PASSWORD=contraseña_postgres
PGADMIN_DEFAULT_PASSWORD=contraseña_pgadmin

# Puertos (opcionales)
FRONTEND_PORT=3000
BACKEND_PORT=8000
```

### Cambiar Credenciales en Producción

1. Edita el archivo `.env`
2. Cambia todas las contraseñas por defecto
3. Usa una API key válida de Google Gemini
4. Genera una SECRET_KEY segura

## 📱 Funcionalidades

### Usuarios
- Registro e inicio de sesión
- Crear y gestionar tickets
- Historial de compras
- Sistema de recompensas y gamificación

### Vendedores
- Dashboard de ventas
- Escáner QR para validar tickets
- CRM para gestión de clientes
- Estadísticas de ventas

### Administradores
- Panel de administración completo
- Gestión de usuarios y vendedores
- CRM con segmentación por IA
- Campañas automáticas con generación de contenido

## 🤖 IA Integrada

- **Procesamiento de tickets**: Análisis automático de tickets con Gemini
- **CRM inteligente**: Segmentación automática de usuarios
- **Generación de contenido**: Creación automática de mensajes de campaña
- **Modelos locales**: Qwen2.5 para generación de texto

## 🛠️ Desarrollo

### Estructura del Proyecto
```
TFG/
├── modules/
│   ├── backend/          # Servicios backend
│   ├── frontend/         # Aplicación React
│   └── databases/        # Configuración de BD
├── docker-compose.yml    # Orquestación de servicios
└── setup-env.ps1        # Script de configuración
```

### Comandos Útiles

```powershell
# Reconstruir un servicio específico
docker compose up -d --build crm-service

# Ver logs de un servicio
docker compose logs crm-service

# Parar todos los servicios
docker compose down

# Parar y eliminar volúmenes
docker compose down -v
```

## 🔒 Seguridad

- Todas las credenciales están externalizadas en variables de entorno
- API keys y secretos no están hardcodeados
- Autenticación JWT implementada
- CORS configurado para desarrollo

## 📄 Licencia

Proyecto de TFG - Universidad
