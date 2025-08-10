# Script para configurar variables de entorno
Write-Host "Configurando variables de entorno para TFG..." -ForegroundColor Green

# Crear archivo .env con variables de entorno básicas
$envContent = @"
# ========================================
# API KEYS
# ========================================
GEMINI_API_KEY=tu_api_key_de_google_gemini_aqui

# ========================================
# SECRETS
# ========================================
SECRET_KEY=genera_una_clave_secreta_segura_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ========================================
# DATABASE CREDENTIALS
# ========================================
POSTGRES_DB=ticket_analytics
POSTGRES_USER=ticket_user
POSTGRES_PASSWORD=genera_una_contraseña_segura_aqui

# ========================================
# PGADMIN CREDENTIALS
# ========================================
PGADMIN_DEFAULT_EMAIL=admin@ticketanalytics.com
PGADMIN_DEFAULT_PASSWORD=genera_una_contraseña_segura_aqui

# ========================================
# SERVICE PORTS
# ========================================
AI_TICKET_PROCESSOR_PORT=8004
TICKET_SERVICE_PORT=8003
BACKEND_PORT=8000
AUTH_SERVICE_PORT=8001
GAMIFICATION_SERVICE_PORT=8005
CRM_SERVICE_PORT=8006
FRONTEND_PORT=3000

# ========================================
# ENVIRONMENT
# ========================================
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
"@

# Escribir el contenido al archivo .env
$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "Archivo .env creado con variables de entorno básicas" -ForegroundColor Green
Write-Host "IMPORTANTE: Debes configurar las siguientes variables antes de usar:" -ForegroundColor Yellow
Write-Host "  - GEMINI_API_KEY: Obtén tu API key de Google Gemini" -ForegroundColor Yellow
Write-Host "  - SECRET_KEY: Genera una clave secreta segura para JWT" -ForegroundColor Yellow
Write-Host "  - POSTGRES_PASSWORD: Establece una contraseña segura para PostgreSQL" -ForegroundColor Yellow
Write-Host "  - PGADMIN_DEFAULT_PASSWORD: Establece una contraseña segura para pgAdmin" -ForegroundColor Yellow

Write-Host "`nConfiguración completada. Edita el archivo .env y luego ejecuta 'docker compose up -d'" -ForegroundColor Green
