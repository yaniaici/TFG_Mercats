# Script para levantar todo el sistema TFG
Write-Host "🚀 Iniciando sistema TFG..." -ForegroundColor Green

# Verificar que Docker esté ejecutándose
try {
    docker version | Out-Null
} catch {
    Write-Host "❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar que el archivo .env existe (opcional)
if (-not (Test-Path ".env")) {
    Write-Host "Advertencia: Archivo .env no encontrado. Asegúrate de tener las variables configuradas." -ForegroundColor Yellow
}

# Iniciar todos los servicios
Write-Host "📦 Iniciando servicios..." -ForegroundColor Yellow
docker-compose up -d

# Esperar a que PostgreSQL esté listo
Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar estado de los servicios
Write-Host "🔍 Verificando estado de los servicios..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "✅ Sistema iniciado!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Servicios disponibles:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend: http://localhost:8000" -ForegroundColor White
Write-Host "   Auth Service: http://localhost:8001" -ForegroundColor White
Write-Host "   Ticket Service: http://localhost:8003" -ForegroundColor White
Write-Host "   Gamification Service: http://localhost:8005" -ForegroundColor White
Write-Host "   CRM Service: http://localhost:8006" -ForegroundColor White
Write-Host "   Notification Sender: http://localhost:8007" -ForegroundColor White
Write-Host "   PgAdmin: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "El CRM service funciona sin VAPID keys (notificaciones solo en BD)" -ForegroundColor Yellow
Write-Host "Para ver logs: docker-compose logs -f [servicio]" -ForegroundColor Gray
Write-Host "Para detener: docker-compose down" -ForegroundColor Gray 