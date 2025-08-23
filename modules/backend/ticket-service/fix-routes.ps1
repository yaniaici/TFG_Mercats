# Script per solucionar problemes de rutes del ticket-service

Write-Host "🔧 Solucionant problemes de rutes del ticket-service..." -ForegroundColor Cyan

# 1. Reiniciar el ticket-service
Write-Host "`n1. Reiniciant ticket-service..." -ForegroundColor Yellow
docker restart tfg_ticket_service

# 2. Esperar que s'iniciï
Write-Host "`n2. Esperant que s'iniciï..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 3. Verificar que està funcionant
Write-Host "`n3. Verificant estat..." -ForegroundColor Yellow
docker ps --filter "name=tfg_ticket_service" --format "table {{.Names}}\t{{.Status}}"

# 4. Verificar logs
Write-Host "`n4. Verificant logs..." -ForegroundColor Yellow
docker logs --tail 10 tfg_ticket_service

# 5. Testejar endpoints
Write-Host "`n5. Testejant endpoints..." -ForegroundColor Yellow

# Health endpoint
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8003/health" -Method Get -TimeoutSec 10
    Write-Host "✅ Health endpoint: $($healthResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health endpoint: $($_.Exception.Message)" -ForegroundColor Red
}

# Historial endpoint
try {
    $historyResponse = Invoke-WebRequest -Uri "http://localhost:8003/tickets/history/test-user" -Method Get -TimeoutSec 10
    Write-Host "✅ Historial endpoint: $($historyResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Historial endpoint: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Verificar via Nginx
Write-Host "`n6. Testejant via Nginx..." -ForegroundColor Yellow
try {
    $nginxResponse = Invoke-WebRequest -Uri "https://mercatmediterrani.com/tickets/history/test-user" -Method Get -TimeoutSec 10 -SkipCertificateCheck
    Write-Host "✅ Nginx proxy: $($nginxResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Nginx proxy: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Verificar configuració de Nginx
Write-Host "`n7. Verificant configuració de Nginx..." -ForegroundColor Yellow
docker exec tfg_postgres nginx -t 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Configuració de Nginx OK" -ForegroundColor Green
} else {
    Write-Host "❌ Error en configuració de Nginx" -ForegroundColor Red
}

Write-Host "`n✅ Procés completat!" -ForegroundColor Green
Write-Host "Si encara hi ha problemes, revisa els logs per més detalls." -ForegroundColor White
