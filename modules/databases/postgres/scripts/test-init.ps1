# Script per testejar la inicialització de PostgreSQL
# Aquest script crea un contenidor temporal per verificar que els scripts funcionen

Write-Host "🧪 Testejant la inicialització de PostgreSQL..." -ForegroundColor Cyan

# Crear un directori temporal per testejar
$testDir = "test-postgres-init"
if (Test-Path $testDir) {
    Remove-Item -Recurse -Force $testDir
}
New-Item -ItemType Directory -Path $testDir

# Crear un docker-compose temporal per testejar
$testCompose = @"
version: "3.8"
services:
  test-postgres:
    build:
      context: ./modules/databases/postgres
      dockerfile: Dockerfile
    container_name: test_postgres
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports:
      - "5433:5432"
    volumes:
      - ./modules/databases/postgres/init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test_user -d test_db"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
"@

$testCompose | Out-File -FilePath "$testDir/docker-compose.yml" -Encoding UTF8

Write-Host "1. Creant contenidor de test..." -ForegroundColor Yellow
Set-Location $testDir
docker-compose up -d

# Esperar que PostgreSQL estigui llest
Write-Host "2. Esperant que PostgreSQL estigui llest..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

do {
    $attempt++
    Start-Sleep -Seconds 2
    
    try {
        $result = docker exec test_postgres pg_isready -U test_user -d test_db 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PostgreSQL està llest!" -ForegroundColor Green
            break
        }
    } catch {
        # Ignorar errors durant la verificació
    }
    
    Write-Host "Intento $attempt/$maxAttempts - Esperant..." -ForegroundColor Yellow
    
} while ($attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    Write-Host "❌ ERROR: PostgreSQL no s'ha pogut inicialitzar en el temps esperat." -ForegroundColor Red
    Set-Location ..
    Remove-Item -Recurse -Force $testDir
    exit 1
}

# Verificar que les taules s'han creat
Write-Host "3. Verificant que les taules s'han creat..." -ForegroundColor Yellow
$tables = docker exec test_postgres psql -U test_user -d test_db -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"

Write-Host "Taules trobades:" -ForegroundColor Green
$tables | ForEach-Object { 
    if ($_.Trim()) { 
        Write-Host "  - $($_.Trim())" -ForegroundColor White 
    } 
}

# Verificar taules específiques
$requiredTables = @("users", "special_rewards", "rewards", "user_gamification")
$missingTables = @()

foreach ($table in $requiredTables) {
    if ($tables -notmatch $table) {
        $missingTables += $table
    }
}

if ($missingTables.Count -gt 0) {
    Write-Host "❌ Taules que falten: $($missingTables -join ', ')" -ForegroundColor Red
} else {
    Write-Host "✅ Totes les taules requerides s'han creat correctament!" -ForegroundColor Green
}

# Verificar dades inicials
Write-Host "4. Verificant dades inicials..." -ForegroundColor Yellow
$adminUser = docker exec test_postgres psql -U test_user -d test_db -t -c "SELECT username, email FROM users WHERE username = 'admin';"
if ($adminUser -match "admin") {
    Write-Host "✅ Usuari administrador creat correctament" -ForegroundColor Green
} else {
    Write-Host "❌ Usuari administrador no trobat" -ForegroundColor Red
}

$specialRewards = docker exec test_postgres psql -U test_user -d test_db -t -c "SELECT COUNT(*) FROM special_rewards;"
if ($specialRewards -match "\d+") {
    Write-Host "✅ Recompenses especials creades: $($specialRewards.Trim())" -ForegroundColor Green
} else {
    Write-Host "❌ Recompenses especials no trobades" -ForegroundColor Red
}

# Netejar
Write-Host "5. Netejant..." -ForegroundColor Yellow
docker-compose down
Set-Location ..
Remove-Item -Recurse -Force $testDir

Write-Host "`n✅ Test completat!" -ForegroundColor Green
Write-Host "Si no hi ha hagut errors, els scripts d'inicialització funcionen correctament." -ForegroundColor Green
