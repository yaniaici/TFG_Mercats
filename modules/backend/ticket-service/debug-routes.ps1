# Script per diagnosticar problemes de rutes del ticket-service

Write-Host "🔍 Diagnosticant problemes de rutes del ticket-service..." -ForegroundColor Cyan

# 1. Verificar que el contenidor està funcionant
Write-Host "`n1. Verificant estat del ticket-service..." -ForegroundColor Yellow
docker ps --filter "name=tfg_ticket_service" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Verificar logs del ticket-service
Write-Host "`n2. Últims logs del ticket-service..." -ForegroundColor Yellow
docker logs --tail 20 tfg_ticket_service

# 3. Testejar l'endpoint de health
Write-Host "`n3. Testejant endpoint de health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8003/health" -Method Get -TimeoutSec 10
    Write-Host "✅ Health endpoint funciona: $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Resposta: $($healthResponse.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Health endpoint no funciona: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Testejar l'endpoint d'historial directament
Write-Host "`n4. Testejant endpoint d'historial directament..." -ForegroundColor Yellow
try {
    $historyResponse = Invoke-WebRequest -Uri "http://localhost:8003/tickets/history/test-user" -Method Get -TimeoutSec 10
    Write-Host "✅ Historial endpoint funciona: $($historyResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Historial endpoint no funciona: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Verificar connexió a la base de dades
Write-Host "`n5. Verificant connexió a la base de dades..." -ForegroundColor Yellow
docker exec tfg_ticket_service python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://ticket_user:ticket_pass@postgres:5432/ticket_analytics')
    print('✅ Connexió a la base de dades OK')
    conn.close()
except Exception as e:
    print(f'❌ Error de connexió: {e}')
"

# 6. Verificar que les taules existeixen
Write-Host "`n6. Verificant taules a la base de dades..." -ForegroundColor Yellow
docker exec tfg_postgres psql -U ticket_user -d ticket_analytics -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('tickets', 'users')
ORDER BY table_name;
"

# 7. Testejar via Nginx
Write-Host "`n7. Testejant via Nginx..." -ForegroundColor Yellow
try {
    $nginxResponse = Invoke-WebRequest -Uri "https://mercatmediterrani.com/tickets/history/test-user" -Method Get -TimeoutSec 10 -SkipCertificateCheck
    Write-Host "✅ Nginx proxy funciona: $($nginxResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Nginx proxy no funciona: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ Diagnòstic completat!" -ForegroundColor Green
Write-Host "Revisa els resultats per identificar el problema." -ForegroundColor White
