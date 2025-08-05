# ========================================
# Docker Manager para TFG Sistema de Mercado
# ========================================

param(
    [Parameter(Position=0)]
    [ValidateSet("up", "down", "restart", "logs", "build", "status", "clean")]
    [string]$Action = "status",
    
    [switch]$Follow,
    [switch]$Force
)

# Colores para output
$Colors = @{
    Info = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Header = "Magenta"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Show-Header {
    Write-ColorOutput "🐳 TFG Docker Manager" "Header"
    Write-ColorOutput "Sistema de Mercado - Gestión de Contenedores" "Info"
    Write-ColorOutput "=============================================" "Info"
    Write-Host ""
}

function Show-Help {
    Write-ColorOutput "📖 Uso del script:" "Header"
    Write-Host ""
    Write-ColorOutput "Comandos principales:" "Info"
    Write-Host "  .\docker-manager.ps1 up              - Iniciar servicio"
    Write-Host "  .\docker-manager.ps1 down            - Parar servicio"
    Write-Host "  .\docker-manager.ps1 restart         - Reiniciar servicio"
    Write-Host "  .\docker-manager.ps1 status          - Mostrar estado del servicio"
    Write-Host "  .\docker-manager.ps1 logs            - Mostrar logs"
    Write-Host "  .\docker-manager.ps1 build           - Construir imagen"
    Write-Host "  .\docker-manager.ps1 clean           - Limpiar todo"
    Write-Host ""
    Write-ColorOutput "Opciones adicionales:" "Info"
    Write-Host "  -Follow                               - Seguir logs en tiempo real"
    Write-Host "  -Force                                - Forzar operación"
    Write-Host ""
    Write-ColorOutput "Ejemplos:" "Info"
    Write-Host "  .\docker-manager.ps1 up"
    Write-Host "  .\docker-manager.ps1 logs -Follow"
    Write-Host "  .\docker-manager.ps1 restart"
}

function Test-DockerCompose {
    try {
        $null = docker-compose --version
        return $true
    }
    catch {
        Write-ColorOutput "❌ Docker Compose no está instalado o no está en el PATH" "Error"
        return $false
    }
}

function Test-Docker {
    try {
        $null = docker --version
        return $true
    }
    catch {
        Write-ColorOutput "❌ Docker no está instalado o no está en el PATH" "Error"
        return $false
    }
}

function Show-Status {
    Write-ColorOutput "📊 Estado del servicio:" "Header"
    Write-Host ""
    
    $service = @{
        Name = "ai-ticket-processor"
        Port = "8003"
        Description = "Procesamiento de tickets con IA"
    }
    
    $containerName = "tfg_ai_ticket_processor"
    $status = docker ps --filter "name=$containerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
    
    if ($status -and $status -notmatch "NAMES") {
        Write-ColorOutput "✅ $($service.Name) (puerto $($service.Port))" "Success"
        Write-Host "   $($service.Description)"
    } else {
        Write-ColorOutput "❌ $($service.Name) (puerto $($service.Port))" "Error"
        Write-Host "   $($service.Description)"
    }
    Write-Host ""
}

function Start-Service {
    Write-ColorOutput "🚀 Iniciando servicio..." "Info"
    
    $command = "docker-compose up -d"
    Write-Host "Ejecutando: $command"
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Servicio iniciado correctamente" "Success"
        Start-Sleep -Seconds 3
        Show-Status
    } else {
        Write-ColorOutput "❌ Error al iniciar servicio" "Error"
    }
}

function Stop-Service {
    Write-ColorOutput "🛑 Parando servicio..." "Info"
    
    $command = "docker-compose down"
    if ($Force) {
        $command += " -v --remove-orphans"
    }
    
    Write-Host "Ejecutando: $command"
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Servicio parado correctamente" "Success"
    } else {
        Write-ColorOutput "❌ Error al parar servicio" "Error"
    }
}

function Restart-Service {
    Write-ColorOutput "🔄 Reiniciando servicio..." "Info"
    
    $command = "docker-compose restart"
    Write-Host "Reiniciando servicio"
    
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Servicio reiniciado correctamente" "Success"
        Start-Sleep -Seconds 2
        Show-Status
    } else {
        Write-ColorOutput "❌ Error al reiniciar servicio" "Error"
    }
}

function Show-Logs {
    Write-ColorOutput "📋 Mostrando logs..." "Info"
    
    $command = "docker-compose logs"
    if ($Follow) {
        $command += " -f"
    }
    
    Write-Host "Ejecutando: $command"
    Invoke-Expression $command
}

function Build-Image {
    Write-ColorOutput "🔨 Construyendo imagen..." "Info"
    
    $command = "docker-compose build"
    if ($Force) {
        $command += " --no-cache"
    }
    
    Write-Host "Ejecutando: $command"
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Imagen construida correctamente" "Success"
    } else {
        Write-ColorOutput "❌ Error al construir imagen" "Error"
    }
}

function Clean-All {
    Write-ColorOutput "🧹 Limpiando todo..." "Warning"
    
    if (-not $Force) {
        Write-ColorOutput "⚠️ Esta acción eliminará todos los contenedores, volúmenes y redes" "Warning"
        $confirmation = Read-Host "¿Estás seguro? (y/N)"
        if ($confirmation -ne "y" -and $confirmation -ne "Y") {
            Write-ColorOutput "❌ Operación cancelada" "Error"
            return
        }
    }
    
    Write-ColorOutput "Parando y eliminando contenedores..." "Info"
    docker-compose down -v --remove-orphans
    
    Write-ColorOutput "Eliminando imágenes no utilizadas..." "Info"
    docker image prune -a -f
    
    Write-ColorOutput "Eliminando volúmenes no utilizados..." "Info"
    docker volume prune -f
    
    Write-ColorOutput "Eliminando redes no utilizadas..." "Info"
    docker network prune -f
    
    Write-ColorOutput "✅ Limpieza completada" "Success"
}

# ========================================
# SCRIPT PRINCIPAL
# ========================================

Show-Header

# Verificar dependencias
if (-not (Test-Docker)) {
    exit 1
}

if (-not (Test-DockerCompose)) {
    exit 1
}

# Verificar si existe docker-compose.yml
if (-not (Test-Path "docker-compose.yml")) {
    Write-ColorOutput "❌ No se encontró docker-compose.yml en el directorio actual" "Error"
    Write-ColorOutput "Ejecuta este script desde el directorio raíz del proyecto" "Info"
    exit 1
}

# Procesar acciones
switch ($Action) {
    "up" {
        Start-Service
    }
    "down" {
        Stop-Service
    }
    "restart" {
        Restart-Service
    }
    "logs" {
        Show-Logs
    }
    "build" {
        Build-Image
    }
    "status" {
        Show-Status
    }
    "clean" {
        Clean-All
    }
    default {
        Show-Help
    }
} 