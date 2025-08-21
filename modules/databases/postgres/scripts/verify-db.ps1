# Script para verificar el estado de la base de datos
# Este script verifica que todas las tablas y datos estén correctos

Write-Host "=== VERIFICACIÓN DE BASE DE DATOS TFG ===" -ForegroundColor Yellow
Write-Host ""

# Verificar si Docker está ejecutándose
try {
    docker version | Out-Null
} catch {
    Write-Host "ERROR: Docker no está ejecutándose. Por favor, inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar si el contenedor de PostgreSQL está ejecutándose
$containerStatus = docker ps --filter "name=tfg-postgres" --format "table {{.Names}}\t{{.Status}}"

if ($containerStatus -notmatch "tfg-postgres") {
    Write-Host "ERROR: El contenedor de PostgreSQL no está ejecutándose." -ForegroundColor Red
    Write-Host "Ejecuta: docker-compose up -d postgres" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Contenedor de PostgreSQL está ejecutándose" -ForegroundColor Green

# Verificar conexión a la base de datos
Write-Host "Verificando conexión a la base de datos..." -ForegroundColor Cyan
$connectionTest = docker exec tfg-postgres-1 pg_isready -U postgres

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Conexión a PostgreSQL exitosa" -ForegroundColor Green
} else {
    Write-Host "✗ ERROR: No se puede conectar a PostgreSQL" -ForegroundColor Red
    exit 1
}

# Listar todas las tablas
Write-Host "Verificando estructura de tablas..." -ForegroundColor Cyan
$tables = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"

Write-Host "Tablas encontradas:" -ForegroundColor White
$tableCount = 0
foreach ($table in $tables -split "`n") {
    $table = $table.Trim()
    if ($table -and $table -ne "table_name") {
        Write-Host "  - $table" -ForegroundColor Gray
        $tableCount++
    }
}

Write-Host "Total de tablas: $tableCount" -ForegroundColor Cyan

# Verificar tablas principales
$mainTables = @("users", "tickets", "stores", "vendors", "roles", "permissions")
$missingTables = @()

foreach ($table in $mainTables) {
    if ($tables -match $table) {
        Write-Host "✓ Tabla '$table' encontrada" -ForegroundColor Green
    } else {
        Write-Host "✗ Tabla '$table' NO encontrada" -ForegroundColor Red
        $missingTables += $table
    }
}

# Verificar datos iniciales
Write-Host "Verificando datos iniciales..." -ForegroundColor Cyan

# Verificar roles
$roles = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT name FROM roles;"
$expectedRoles = @("admin", "vendor", "user", "support")
$missingRoles = @()

foreach ($role in $expectedRoles) {
    if ($roles -match $role) {
        Write-Host "✓ Rol '$role' encontrado" -ForegroundColor Green
    } else {
        Write-Host "✗ Rol '$role' NO encontrado" -ForegroundColor Red
        $missingRoles += $role
    }
}

# Verificar usuario administrador
$adminUser = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT username, email FROM users WHERE username = 'admin';"

if ($adminUser -match "admin") {
    Write-Host "✓ Usuario administrador encontrado" -ForegroundColor Green
    Write-Host "  Usuario: admin" -ForegroundColor White
    Write-Host "  Email: admin@tfg.com" -ForegroundColor White
} else {
    Write-Host "✗ Usuario administrador NO encontrado" -ForegroundColor Red
}

# Verificar permisos
$permissions = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT COUNT(*) as total FROM permissions;"
$permissionCount = ($permissions -split "`n" | Where-Object { $_ -match "^\s*\d+\s*$" } | ForEach-Object { $_.Trim() })[0]

if ($permissionCount -gt 0) {
    Write-Host "✓ $permissionCount permisos encontrados" -ForegroundColor Green
} else {
    Write-Host "✗ No se encontraron permisos" -ForegroundColor Red
}

# Resumen
Write-Host ""
Write-Host "=== RESUMEN DE VERIFICACIÓN ===" -ForegroundColor Yellow

if ($missingTables.Count -eq 0) {
    Write-Host "✓ Todas las tablas principales están presentes" -ForegroundColor Green
} else {
    Write-Host "✗ Faltan las siguientes tablas: $($missingTables -join ', ')" -ForegroundColor Red
}

if ($missingRoles.Count -eq 0) {
    Write-Host "✓ Todos los roles están presentes" -ForegroundColor Green
} else {
    Write-Host "✗ Faltan los siguientes roles: $($missingRoles -join ', ')" -ForegroundColor Red
}

if ($adminUser -match "admin") {
    Write-Host "✓ Usuario administrador está configurado" -ForegroundColor Green
} else {
    Write-Host "✗ Usuario administrador no está configurado" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== VERIFICACIÓN COMPLETADA ===" -ForegroundColor Green
