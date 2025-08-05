# Script para iniciar el frontend en modo desarrollo
Write-Host "🚀 Iniciando Frontend TFG en modo desarrollo..." -ForegroundColor Green

# Verificar si Node.js está instalado
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js no está instalado. Por favor instala Node.js desde https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Verificar si npm está disponible
try {
    $npmVersion = npm --version
    Write-Host "✅ npm encontrado: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm no está disponible" -ForegroundColor Red
    exit 1
}

# Verificar si las dependencias están instaladas
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
        exit 1
    }
}

# Iniciar el servidor de desarrollo
Write-Host "🌐 Iniciando servidor de desarrollo en http://localhost:3000" -ForegroundColor Green
Write-Host "📱 El frontend estará disponible en tu navegador" -ForegroundColor Cyan
Write-Host "🔄 Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow

npm start 