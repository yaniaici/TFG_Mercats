# Script para manejar el contenedor AI Ticket Processor (PowerShell)

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Colores para output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Función para mostrar ayuda
function Show-Help {
    Write-Host "AI Ticket Processor - Docker Manager" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Uso: .\docker-run.ps1 [COMANDO]"
    Write-Host ""
    Write-Host "Comandos disponibles:"
    Write-Host "  build     - Construir la imagen Docker"
    Write-Host "  run       - Ejecutar el contenedor"
    Write-Host "  stop      - Detener el contenedor"
    Write-Host "  restart   - Reiniciar el contenedor"
    Write-Host "  logs      - Mostrar logs del contenedor"
    Write-Host "  test      - Probar el servicio"
    Write-Host "  clean     - Limpiar contenedores e imágenes"
    Write-Host "  help      - Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:"
    Write-Host "  .\docker-run.ps1 build"
    Write-Host "  .\docker-run.ps1 run"
    Write-Host "  .\docker-run.ps1 test"
}

# Función para construir la imagen
function Build-Image {
    Write-Host "🔨 Construyendo imagen Docker..." -ForegroundColor $Blue
    docker build -t ai-ticket-processor .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Imagen construida exitosamente" -ForegroundColor $Green
    } else {
        Write-Host "❌ Error construyendo imagen" -ForegroundColor $Red
        exit 1
    }
}

# Función para ejecutar el contenedor
function Run-Container {
    Write-Host "🚀 Ejecutando contenedor..." -ForegroundColor $Blue
    
    # Verificar si existe el archivo .env
    if (-not (Test-Path ".env")) {
        Write-Host "❌ Archivo .env no encontrado en el directorio actual" -ForegroundColor $Red
        Write-Host "⚠️  Por favor, crea un archivo .env con tu API key de Gemini" -ForegroundColor $Yellow
        Write-Host "📋 Ejemplo: GEMINI_API_KEY=tu_api_key_aqui" -ForegroundColor $Blue
        exit 1
    }
    
    # Detener contenedor si está ejecutándose
    docker stop ai-ticket-processor 2>$null
    docker rm ai-ticket-processor 2>$null
    
    # Ejecutar contenedor
    docker run -d `
        --name ai-ticket-processor `
        --env-file .env `
        -p 8003:8003 `
        -v "${PWD}\images:/app/images:ro" `
        ai-ticket-processor
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Contenedor ejecutándose en http://localhost:8003" -ForegroundColor $Green
        Write-Host "📋 Para ver logs: .\docker-run.ps1 logs" -ForegroundColor $Blue
    } else {
        Write-Host "❌ Error ejecutando contenedor" -ForegroundColor $Red
        exit 1
    }
}

# Función para detener el contenedor
function Stop-Container {
    Write-Host "🛑 Deteniendo contenedor..." -ForegroundColor $Blue
    docker stop ai-ticket-processor 2>$null
    docker rm ai-ticket-processor 2>$null
    Write-Host "✅ Contenedor detenido" -ForegroundColor $Green
}

# Función para reiniciar el contenedor
function Restart-Container {
    Write-Host "🔄 Reiniciando contenedor..." -ForegroundColor $Blue
    Stop-Container
    Run-Container
}

# Función para mostrar logs
function Show-Logs {
    Write-Host "📋 Mostrando logs del contenedor..." -ForegroundColor $Blue
    docker logs -f ai-ticket-processor
}

# Función para probar el servicio
function Test-Service {
    Write-Host "🧪 Probando servicio..." -ForegroundColor $Blue
    
    # Esperar un momento para que el servicio se inicie
    Start-Sleep -Seconds 3
    
    # Probar health check
    Write-Host "📡 Probando health check..." -ForegroundColor $Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8003/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Health check exitoso" -ForegroundColor $Green
        } else {
            Write-Host "❌ Health check falló" -ForegroundColor $Red
            return
        }
    } catch {
        Write-Host "❌ Health check falló: $($_.Exception.Message)" -ForegroundColor $Red
        return
    }
    
    # Probar información del modelo
    Write-Host "🤖 Probando información del modelo..." -ForegroundColor $Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8003/model-info" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Modelo funcionando correctamente" -ForegroundColor $Green
        } else {
            Write-Host "❌ Error obteniendo información del modelo" -ForegroundColor $Red
            return
        }
    } catch {
        Write-Host "❌ Error obteniendo información del modelo: $($_.Exception.Message)" -ForegroundColor $Red
        return
    }
    
    Write-Host "🎉 Servicio funcionando correctamente!" -ForegroundColor $Green
    Write-Host "📋 Endpoints disponibles:" -ForegroundColor $Blue
    Write-Host "  - Health: http://localhost:8003/health"
    Write-Host "  - Model Info: http://localhost:8003/model-info"
    Write-Host "  - Process Ticket: http://localhost:8003/process-ticket"
}

# Función para limpiar
function Clean-Docker {
    Write-Host "🧹 Limpiando Docker..." -ForegroundColor $Blue
    docker stop ai-ticket-processor 2>$null
    docker rm ai-ticket-processor 2>$null
    docker rmi ai-ticket-processor 2>$null
    Write-Host "✅ Limpieza completada" -ForegroundColor $Green
}

# Manejo de comandos
switch ($Command.ToLower()) {
    "build" { Build-Image }
    "run" { Run-Container }
    "stop" { Stop-Container }
    "restart" { Restart-Container }
    "logs" { Show-Logs }
    "test" { Test-Service }
    "clean" { Clean-Docker }
    default { Show-Help }
} 