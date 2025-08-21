# Script para reinicializar completamente la base de datos
# Este script elimina y recrea el contenedor de PostgreSQL

Write-Host "=== REINICIALIZACIÓN DE BASE DE DATOS TFG ===" -ForegroundColor Yellow
Write-Host ""

# Verificar si Docker está ejecutándose
try {
    docker version | Out-Null
} catch {
    Write-Host "ERROR: Docker no está ejecutándose. Por favor, inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Detener y eliminar el contenedor de PostgreSQL si existe
Write-Host "Deteniendo contenedor de PostgreSQL..." -ForegroundColor Cyan
docker-compose -f ../../../docker-compose.yml stop postgres 2>$null
docker-compose -f ../../../docker-compose.yml rm -f postgres 2>$null

# Eliminar el volumen de datos si existe
Write-Host "Eliminando volumen de datos..." -ForegroundColor Cyan
docker volume rm tfg_postgres_data 2>$null

# Recrear el contenedor
Write-Host "Recreando contenedor de PostgreSQL..." -ForegroundColor Cyan
docker-compose -f ../../../docker-compose.yml up -d postgres

# Esperar a que PostgreSQL esté listo
Write-Host "Esperando a que PostgreSQL esté listo..." -ForegroundColor Cyan
$maxAttempts = 30
$attempt = 0

do {
    $attempt++
    Start-Sleep -Seconds 2
    
    try {
        $result = docker exec tfg-postgres-1 pg_isready -U postgres 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PostgreSQL está listo!" -ForegroundColor Green
            break
        }
    } catch {
        # Ignorar errores durante la verificación
    }
    
    Write-Host "Intento $attempt/$maxAttempts - Esperando..." -ForegroundColor Yellow
    
} while ($attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    Write-Host "ERROR: PostgreSQL no se pudo inicializar en el tiempo esperado." -ForegroundColor Red
    exit 1
}

# Verificar que las tablas se crearon correctamente
Write-Host "Verificando estructura de la base de datos..." -ForegroundColor Cyan
$tables = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"

if ($tables -match "users") {
    Write-Host "✓ Tabla 'users' creada correctamente" -ForegroundColor Green
} else {
    Write-Host "✗ ERROR: Tabla 'users' no encontrada" -ForegroundColor Red
}

if ($tables -match "tickets") {
    Write-Host "✓ Tabla 'tickets' creada correctamente" -ForegroundColor Green
} else {
    Write-Host "✗ ERROR: Tabla 'tickets' no encontrada" -ForegroundColor Red
}

if ($tables -match "roles") {
    Write-Host "✓ Tabla 'roles' creada correctamente" -ForegroundColor Green
} else {
    Write-Host "✗ ERROR: Tabla 'roles' no encontrada" -ForegroundColor Red
}

# Verificar usuario administrador
Write-Host "Verificando usuario administrador..." -ForegroundColor Cyan
$adminUser = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT username, email FROM users WHERE username = 'admin';"

if ($adminUser -match "admin") {
    Write-Host "✓ Usuario administrador creado correctamente" -ForegroundColor Green
    Write-Host "  Usuario: admin" -ForegroundColor White
    Write-Host "  Email: admin@tfg.com" -ForegroundColor White
    Write-Host "  Contraseña: admin123" -ForegroundColor White
} else {
    Write-Host "✗ ERROR: Usuario administrador no encontrado" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== REINICIALIZACIÓN COMPLETADA ===" -ForegroundColor Green
Write-Host "La base de datos ha sido reinicializada correctamente." -ForegroundColor White
Write-Host "IMPORTANTE: Cambia la contraseña del administrador en producción." -ForegroundColor Yellow
Write-Host "" 