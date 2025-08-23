# Script per verificar que la inicialització de la base de dades ha funcionat correctament
# Executar després de docker-compose up -d

Write-Host "🔍 Verificant la inicialització de la base de dades..." -ForegroundColor Cyan

# Verificar que el contenidor PostgreSQL està funcionant
Write-Host "1. Verificant que PostgreSQL està funcionant..." -ForegroundColor Yellow
docker ps --filter "name=tfg_postgres" --format "table {{.Names}}\t{{.Status}}"

# Verificar que les taules principals existeixen
Write-Host "`n2. Verificant que les taules principals existeixen..." -ForegroundColor Yellow
docker exec tfg_postgres psql -U postgres -d mercatmediterrani -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
"

# Verificar que la taula special_rewards existeix i té dades
Write-Host "`n3. Verificant la taula special_rewards..." -ForegroundColor Yellow
docker exec tfg_postgres psql -U postgres -d mercatmediterrani -c "
SELECT name, description, is_active 
FROM special_rewards 
ORDER BY created_at;
"

# Verificar que hi ha dades d'usuari
Write-Host "`n4. Verificant dades d'usuari..." -ForegroundColor Yellow
docker exec tfg_postgres psql -U postgres -d mercatmediterrani -c "
SELECT COUNT(*) as total_users FROM users;
"

# Verificar que hi ha recompenses
Write-Host "`n5. Verificant recompenses..." -ForegroundColor Yellow
docker exec tfg_postgres psql -U postgres -d mercatmediterrani -c "
SELECT COUNT(*) as total_rewards FROM rewards;
"

Write-Host "`n✅ Verificació completada!" -ForegroundColor Green
Write-Host "Si totes les taules existeixen i tenen dades, la inicialització ha funcionat correctament." -ForegroundColor Green
