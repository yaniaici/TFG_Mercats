# Script para verificar si las recompensas se cargaron correctamente
Write-Host "=== VERIFICACIÓN DE RECOMPENSAS ===" -ForegroundColor Yellow
Write-Host ""

# Verificar si PostgreSQL está ejecutándose
try {
    $result = docker exec tfg-postgres-1 pg_isready -U postgres 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: PostgreSQL no está ejecutándose" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: No se puede conectar a PostgreSQL" -ForegroundColor Red
    exit 1
}

Write-Host "✓ PostgreSQL está ejecutándose" -ForegroundColor Green

# Verificar si la tabla rewards existe
Write-Host "Verificando tabla rewards..." -ForegroundColor Cyan
$tableExists = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rewards');"

if ($tableExists -match "t") {
    Write-Host "✓ Tabla rewards existe" -ForegroundColor Green
} else {
    Write-Host "✗ ERROR: Tabla rewards no existe" -ForegroundColor Red
    exit 1
}

# Verificar cuántas recompensas hay
Write-Host "Contando recompensas..." -ForegroundColor Cyan
$rewardCount = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT COUNT(*) FROM rewards;"

if ($rewardCount -match "\d+") {
    $count = [int]$rewardCount.Trim()
    Write-Host "✓ Se encontraron $count recompensas" -ForegroundColor Green
    
    if ($count -eq 0) {
        Write-Host "⚠ ADVERTENCIA: No hay recompensas en la tabla" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ ERROR: No se pudo contar las recompensas" -ForegroundColor Red
}

# Mostrar algunas recompensas como ejemplo
Write-Host "Mostrando primeras 5 recompensas:" -ForegroundColor Cyan
$rewards = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT name, points_cost, reward_type FROM rewards LIMIT 5;"

if ($rewards) {
    $rewards -split "`n" | Where-Object { $_.Trim() -ne "" } | ForEach-Object {
        $parts = $_ -split "\|"
        if ($parts.Length -ge 3) {
            $name = $parts[0].Trim()
            $points = $parts[1].Trim()
            $type = $parts[2].Trim()
            Write-Host "  - $name ($points puntos, tipo: $type)" -ForegroundColor White
        }
    }
} else {
    Write-Host "  No se encontraron recompensas para mostrar" -ForegroundColor Yellow
}

# Verificar tipos de recompensas
Write-Host "Tipos de recompensas disponibles:" -ForegroundColor Cyan
$types = docker exec tfg-postgres-1 psql -U postgres -d tfg_db -t -c "SELECT DISTINCT reward_type, COUNT(*) as count FROM rewards GROUP BY reward_type;"

if ($types) {
    $types -split "`n" | Where-Object { $_.Trim() -ne "" } | ForEach-Object {
        $parts = $_ -split "\|"
        if ($parts.Length -ge 2) {
            $type = $parts[0].Trim()
            $count = $parts[1].Trim()
            Write-Host "  - $type : $count recompensas" -ForegroundColor White
        }
    }
} else {
    Write-Host "  No se encontraron tipos de recompensas" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== VERIFICACIÓN COMPLETADA ===" -ForegroundColor Green
