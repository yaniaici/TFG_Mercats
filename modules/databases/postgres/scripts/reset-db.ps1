# Script para resetear completamente la base de datos PostgreSQL
# Ejecutar desde la raíz del proyecto (donde está el docker-compose.yml)

Write-Host "⚠️  ADVERTENCIA: Esto eliminará TODOS los datos de la base de datos!" -ForegroundColor Red
Write-Host "¿Estás seguro de que quieres continuar? (y/N)" -ForegroundColor Yellow
$confirmation = Read-Host

if ($confirmation -ne "y" -and $confirmation -ne "Y") {
    Write-Host "❌ Operación cancelada." -ForegroundColor Red
    exit 0
}

Write-Host "🔄 Reseteando base de datos PostgreSQL..." -ForegroundColor Yellow

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: No se encontró docker-compose.yml. Ejecuta este script desde la raíz del proyecto." -ForegroundColor Red
    exit 1
}

# Detener y eliminar solo los servicios de base de datos
Write-Host "📦 Deteniendo servicios de base de datos..." -ForegroundColor Yellow
docker-compose stop postgres pgadmin
docker-compose rm -f postgres pgadmin

# Eliminar volúmenes de base de datos
Write-Host "🗑️  Eliminando volúmenes de datos..." -ForegroundColor Yellow
docker volume rm tfg_postgres_data 2>$null
docker volume rm tfg_pgadmin_data 2>$null

# Eliminar imágenes relacionadas
Write-Host "🗑️  Eliminando imágenes..." -ForegroundColor Yellow
docker rmi tfg_postgres 2>$null
docker rmi dpage/pgadmin4 2>$null

# Limpiar contenedores huérfanos
Write-Host "🧹 Limpiando contenedores huérfanos..." -ForegroundColor Yellow
docker container prune -f

# Reconstruir e iniciar solo los servicios de base de datos
Write-Host "🔨 Reconstruyendo e iniciando servicios de base de datos..." -ForegroundColor Yellow
docker-compose up -d postgres pgadmin

# Esperar a que PostgreSQL esté listo
Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Verificar el estado
Write-Host "🔍 Verificando estado de los servicios..." -ForegroundColor Yellow
docker-compose ps postgres pgadmin

Write-Host ""
Write-Host "✅ Base de datos reseteada correctamente!" -ForegroundColor Green
Write-Host "📊 La base de datos está lista para usar con las tablas inicializadas." -ForegroundColor Cyan 