# Script para detener la base de datos PostgreSQL
# Ejecutar desde la raíz del proyecto (donde está el docker-compose.yml)

Write-Host "🛑 Deteniendo base de datos PostgreSQL..." -ForegroundColor Yellow

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: No se encontró docker-compose.yml. Ejecuta este script desde la raíz del proyecto." -ForegroundColor Red
    exit 1
}

# Detener solo los servicios de base de datos
Write-Host "📦 Deteniendo servicios de base de datos..." -ForegroundColor Yellow
docker-compose stop postgres pgadmin

# Verificar que los servicios se han detenido
Write-Host "🔍 Verificando estado de los servicios..." -ForegroundColor Yellow
docker-compose ps postgres pgadmin

Write-Host ""
Write-Host "✅ Base de datos detenida correctamente!" -ForegroundColor Green
Write-Host "💡 Para eliminar también los volúmenes de datos, ejecuta: docker-compose down -v" -ForegroundColor Cyan 