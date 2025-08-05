# Script para iniciar la base de datos PostgreSQL
# Ejecutar desde la raíz del proyecto (donde está el docker-compose.yml)

Write-Host "🚀 Iniciando base de datos PostgreSQL para Ticket Analytics..." -ForegroundColor Green

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: No se encontró docker-compose.yml. Ejecuta este script desde la raíz del proyecto." -ForegroundColor Red
    exit 1
}

# Verificar si Docker está ejecutándose
try {
    docker version | Out-Null
    Write-Host "✅ Docker está ejecutándose" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker no está ejecutándose. Por favor, inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Construir e iniciar solo los servicios de base de datos
Write-Host "📦 Construyendo e iniciando servicios de base de datos..." -ForegroundColor Yellow
docker-compose up -d postgres pgadmin

# Esperar a que PostgreSQL esté listo
Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar el estado de los servicios
Write-Host "🔍 Verificando estado de los servicios..." -ForegroundColor Yellow
docker-compose ps postgres pgadmin

# Mostrar información de conexión
Write-Host ""
Write-Host "📊 Información de conexión:" -ForegroundColor Cyan
Write-Host "   Base de datos: ticket_analytics" -ForegroundColor White
Write-Host "   Usuario: ticket_user" -ForegroundColor White
Write-Host "   Contraseña: ticket_password" -ForegroundColor White
Write-Host "   Puerto: 5432" -ForegroundColor White
Write-Host "   PgAdmin: http://localhost:8080" -ForegroundColor White
Write-Host "   PgAdmin Email: admin@ticketanalytics.com" -ForegroundColor White
Write-Host "   PgAdmin Password: admin123" -ForegroundColor White

Write-Host ""
Write-Host "✅ Base de datos iniciada correctamente!" -ForegroundColor Green 