# Script per reinicialitzar completament la base de dades
# ATENCIÓ: Això eliminarà totes les dades existents!

Write-Host "⚠️  ATENCIÓ: Aquest script eliminarà totes les dades de la base de dades!" -ForegroundColor Red
Write-Host "Si estàs segur que vols continuar, escriu 'SI' per confirmar:" -ForegroundColor Yellow

$confirmacio = Read-Host

if ($confirmacio -ne "SI") {
    Write-Host "❌ Operació cancel·lada." -ForegroundColor Red
    exit
}

Write-Host "🔄 Reinicialitzant la base de dades..." -ForegroundColor Cyan

# Aturar els serveis
Write-Host "1. Aturant els serveis..." -ForegroundColor Yellow
docker-compose down

# Eliminar el volum de PostgreSQL
Write-Host "2. Eliminant el volum de PostgreSQL..." -ForegroundColor Yellow
docker volume rm TFG_Mercats_postgres_data

# Reiniciar els serveis
Write-Host "3. Reiniciant els serveis..." -ForegroundColor Yellow
docker-compose up -d

# Esperar que PostgreSQL estigui llest
Write-Host "4. Esperant que PostgreSQL estigui llest..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verificar que tot funciona
Write-Host "5. Verificant la inicialització..." -ForegroundColor Yellow
& "$PSScriptRoot\verify-db-init.ps1"

Write-Host "`n✅ Base de dades reinicialitzada correctament!" -ForegroundColor Green
Write-Host "Totes les taules s'han creat i les dades inicials s'han inserit." -ForegroundColor Green 