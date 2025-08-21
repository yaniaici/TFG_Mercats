# Script para configurar el archivo hosts
# Ejecutar como administrador

Write-Host "🌐 Configurando dominio local mercatmediterrani.com..." -ForegroundColor Green

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$domainEntries = @(
    "127.0.0.1 mercatmediterrani.com",
    "127.0.0.1 www.mercatmediterrani.com",
    "127.0.0.1 api.mercatmediterrani.com"
)

Write-Host "📝 Añadiendo entradas al archivo hosts..." -ForegroundColor Yellow

try {
    $hostsContent = Get-Content $hostsPath
    $newEntries = $hostsContent + $domainEntries
    $newEntries | Set-Content $hostsPath -Force
    Write-Host "✅ Archivo hosts configurado correctamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Asegúrate de ejecutar este script como administrador" -ForegroundColor Yellow
    exit 1
}

Write-Host "🎉 ¡Dominio configurado!" -ForegroundColor Green
Write-Host "🌐 Ahora puedes acceder a:" -ForegroundColor Cyan
Write-Host "   • http://mercatmediterrani.com" -ForegroundColor White
Write-Host "   • http://www.mercatmediterrani.com" -ForegroundColor White
Write-Host "   • http://api.mercatmediterrani.com" -ForegroundColor White
