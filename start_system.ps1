# Script para levantar todo el sistema TFG
Write-Host "🚀 LEVANTANDO SISTEMA TFG COMPLETO" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Detener contenedores existentes si los hay
Write-Host "🛑 Deteniendo contenedores existentes..." -ForegroundColor Yellow
docker-compose down

# Limpiar volúmenes si es necesario (descomentar para reset completo)
# Write-Host "🧹 Limpiando volúmenes..." -ForegroundColor Yellow
# docker-compose down -v

# Construir y levantar todos los servicios
Write-Host "🔨 Construyendo y levantando servicios..." -ForegroundColor Yellow
docker-compose up --build -d

# Esperar a que los servicios estén listos
Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Mostrar estado de los contenedores
Write-Host "📊 Estado de los contenedores:" -ForegroundColor Cyan
docker-compose ps

# Verificar health checks
Write-Host "🏥 Verificando health checks..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Mostrar logs de los servicios principales
Write-Host "📋 Logs de los servicios principales:" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔐 Auth Service:" -ForegroundColor Green
docker-compose logs --tail=10 auth-service

Write-Host "🎫 Ticket Service:" -ForegroundColor Green
docker-compose logs --tail=10 ticket-service

Write-Host "🤖 AI Ticket Processor:" -ForegroundColor Green
docker-compose logs --tail=10 ai-ticket-processor

Write-Host "🌐 Frontend:" -ForegroundColor Green
docker-compose logs --tail=10 frontend

# Mostrar URLs de acceso
Write-Host ""
Write-Host "🌐 URLs DE ACCESO:" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Auth Service: http://localhost:8001" -ForegroundColor Cyan
Write-Host "Ticket Service: http://localhost:8003" -ForegroundColor Cyan
Write-Host "AI Ticket Processor: http://localhost:8004" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "PgAdmin: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  - Email: admin@ticketanalytics.com" -ForegroundColor White
Write-Host "  - Password: admin123" -ForegroundColor White

Write-Host ""
Write-Host "✅ Sistema levantado correctamente!" -ForegroundColor Green
Write-Host ""

# Preguntar si quiere ejecutar el procesamiento de tickets
$response = Read-Host "¿Quieres ejecutar el procesamiento de tickets pendientes? (s/n)"
if ($response -eq "s" -or $response -eq "S") {
    Write-Host "🎫 Ejecutando procesamiento de tickets..." -ForegroundColor Yellow
    python process_tickets_after_startup.py
}

Write-Host ""
Write-Host "🎉 ¡Sistema listo para usar!" -ForegroundColor Green 