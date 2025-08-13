# 🏪 Mercat Mediterrani - Aplicación de Gamificación y Análisis para mercados

Sistema completo de gestión de tickets digitales para mercados, con gamificación, IA y CRM integrado. Desarrollado como Trabajo de Fin de Grado (TFG).

## 🚀 Características Principales

### 📱 **Frontend (React + TypeScript)**
- **Interfaz completamente en catalán** 🇨🇦
- Diseño responsive y moderno
- Sistema de autenticación JWT
- Escáner de tickets con cámara
- Panel de usuario con gamificación
- Panel de vendedor con QR scanner
- Panel de administrador
- Sistema de recompensas y puntos

### 🔧 **Backend (FastAPI + Python)**
- **6 microservicios** especializados
- Autenticación y autorización
- Procesamiento de IA con Gemini
- Sistema de gamificación
- CRM para gestión de clientes
- Gestión de tickets digitales
- Base de datos PostgreSQL

### 🤖 **Inteligencia Artificial**
- Procesamiento automático de tickets
- Análisis de compras con Gemini AI
- Segmentación automática de clientes
- Recomendaciones personalizadas

### 🎮 **Gamificación**
- Sistema de puntos por compras
- Recompensas canjeables
- Badges y logros
- Historial de actividad

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Auth Service  │    │  Ticket Service │
│   (React)       │◄──►│   (Port 8001)   │◄──►│   (Port 8003)   │
│   (Port 3000)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │  Main Backend   │              │
         │              │   (Port 8000)   │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │ Gamification    │              │
         │              │   (Port 8005)   │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   CRM Service   │              │
         │              │   (Port 8006)   │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │ AI Processor    │              │
         │              │   (Port 8004)   │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   PostgreSQL    │              │
         │              │   (Port 5432)   │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     Ollama      │              │
         │              │   (Port 11434)  │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │    PgAdmin      │              │
         │              │   (Port 8080)   │              │
         │              └─────────────────┘              │
         └──────────────┴─────────────────┴──────────────┘
```

## 🛠️ Tecnologías Utilizadas

### Frontend
- **React 18** con TypeScript
- **Tailwind CSS** para estilos
- **React Router** para navegación
- **Axios** para peticiones HTTP
- **React Hook Form** para formularios
- **Lucide React** para iconos

### Backend
- **FastAPI** (Python 3.11)
- **SQLAlchemy** ORM
- **PostgreSQL** base de datos
- **JWT** autenticación
- **Pydantic** validación de datos
- **Uvicorn** servidor ASGI

### IA y Procesamiento
- **Google Gemini AI** para análisis
- **Ollama** para IA local
- **OpenCV** para procesamiento de imágenes
- **Pillow** para manipulación de imágenes

### DevOps
- **Docker** y **Docker Compose**
- **Nginx** para servidor web
- **PowerShell** scripts de automatización

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose
- PowerShell (Windows)
- API Key de Google Gemini

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd TFG
```

### 2. Configurar variables de entorno
```powershell
# Ejecutar script de configuración
.\setup-env.ps1

# O crear manualmente el archivo .env
```

### 3. Configurar API Key de Gemini
Editar el archivo `.env` y añadir tu API key:
```
GEMINI_API_KEY=tu_api_key_de_google_gemini_aqui
```

### 4. Levantar el sistema
```powershell
# Levantar todos los servicios
.\start_system.ps1

# O manualmente
docker-compose up --build -d
```

### 5. Acceder al sistema
- **Frontend**: http://localhost:3000
- **PgAdmin**: http://localhost:8080
  - Email: `admin@ticketanalytics.com`
  - Contraseña: `admin123`

## 📊 Servicios del Sistema

### 🔐 Auth Service (Puerto 8001)
- Autenticación JWT
- Registro de usuarios y vendedores
- Gestión de sesiones
- Historial de compras

### 🎫 Ticket Service (Puerto 8003)
- Gestión de tickets digitales
- Escaneo y procesamiento
- Integración con gamificación
- Servicio de tiendas del mercado

### 🎮 Gamification Service (Puerto 8005)
- Sistema de puntos
- Recompensas canjeables
- Badges y logros
- Estadísticas de usuario

### 🤖 AI Ticket Processor (Puerto 8004)
- Procesamiento automático de tickets
- Análisis con Gemini AI
- Extracción de datos
- Validación automática

### 👥 CRM Service (Puerto 8006)
- Gestión de clientes
- Segmentación automática
- Campañas de marketing
- Análisis de preferencias

### 🏢 Main Backend (Puerto 8000)
- API principal
- Gestión de usuarios
- Estadísticas generales
- Coordinación entre servicios

## 🎯 Funcionalidades por Rol

### 👤 **Usuario Final**
- Registro e inicio de sesión
- Escaneo de tickets con cámara
- Visualización de puntos y recompensas
- Historial de compras
- Canje de recompensas
- QR personal para recibir tickets

### 🏪 **Vendedor**
- Panel de vendedor
- QR scanner para validar recompensas
- Envío de tickets digitales
- Gestión de clientes
- Estadísticas de ventas

### 👨‍💼 **Administrador**
- Gestión de usuarios
- Configuración del sistema
- Campañas de CRM
- Estadísticas globales
- Gestión de recompensas

## 🗄️ Base de Datos

### Tablas Principales
- `users` - Usuarios del sistema
- `tickets` - Tickets digitales
- `rewards` - Recompensas disponibles
- `reward_redemptions` - Canjes de recompensas
- `user_stats` - Estadísticas de gamificación
- `market_stores` - Tiendas del mercado
- `purchase_history` - Historial de compras

### Acceso a Base de Datos
- **Host**: localhost:5432
- **Base de datos**: ticket_analytics
- **Usuario**: ticket_user
- **Contraseña**: password_segura_2024

## 🔧 Comandos Útiles

### Gestión de Docker
```powershell
# Ver estado de servicios
docker-compose ps

# Ver logs de un servicio
docker-compose logs -f [service-name]

# Reiniciar un servicio
docker-compose restart [service-name]

# Parar todos los servicios
docker-compose down

# Reconstruir y levantar
docker-compose up --build -d
```

### Gestión de Base de Datos
```powershell
# Acceder a PostgreSQL
docker-compose exec postgres psql -U ticket_user -d ticket_analytics

# Resetear base de datos
.\modules\databases\postgres\scripts\reset-db.ps1

# Inicializar recompensas
docker-compose exec gamification-service python init_rewards.py
```

### Desarrollo Frontend
```powershell
# Instalar dependencias
cd modules/frontend
npm install

# Ejecutar en modo desarrollo
npm start

# Construir para producción
npm run build
```

## 🐛 Solución de Problemas

### Servicios no inician
1. Verificar que Docker esté ejecutándose
2. Comprobar variables de entorno en `.env`
3. Verificar puertos disponibles
4. Revisar logs: `docker-compose logs [service-name]`

### Problemas de conexión
1. Verificar que todos los servicios estén "healthy"
2. Comprobar configuración de red Docker
3. Verificar firewall y antivirus

### Problemas de IA
1. Verificar API Key de Gemini
2. Comprobar conexión a Ollama
3. Revisar logs del AI Processor

## 📝 Notas de Desarrollo

### Estructura de Archivos
```
TFG/
├── docker-compose.yml          # Configuración de servicios
├── setup-env.ps1              # Script de configuración
├── start_system.ps1           # Script de inicio
├── .env                       # Variables de entorno
├── modules/
│   ├── frontend/              # Aplicación React
│   ├── backend/               # Microservicios
│   └── databases/             # Configuración de BD
└── README.md                  # Este archivo
```

### Convenciones de Código
- **Frontend**: TypeScript, componentes funcionales, hooks
- **Backend**: Python, FastAPI, async/await
- **Base de datos**: SQLAlchemy, migraciones automáticas
- **Documentación**: Comentarios en catalán

### Seguridad
- Autenticación JWT con expiración
- Validación de datos con Pydantic
- Variables de entorno para secretos
- CORS configurado correctamente

## 📄 Licencia

Este proyecto es un Trabajo de Fin de Grado (TFG) desarrollado para la Universitat Rovira i Virgili.

## 👥 Autores

- **Desarrollador**: Yani Aici
- **Universidad**: Universitat Rovira i Virgili
- **Año**: 2025

---

**Mercat Mediterrani** - Sistema de Gestión de Tickets Digitales con IA y Gamificación 🏪✨
