#!/bin/bash

# Script para manejar el contenedor AI Ticket Processor

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}AI Ticket Processor - Docker Manager${NC}"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  build     - Construir la imagen Docker"
    echo "  run       - Ejecutar el contenedor"
    echo "  stop      - Detener el contenedor"
    echo "  restart   - Reiniciar el contenedor"
    echo "  logs      - Mostrar logs del contenedor"
    echo "  test      - Probar el servicio"
    echo "  clean     - Limpiar contenedores e imágenes"
    echo "  help      - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 test"
}

# Función para construir la imagen
build_image() {
    echo -e "${BLUE}🔨 Construyendo imagen Docker...${NC}"
    docker build -t ai-ticket-processor .
    echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"
}

# Función para ejecutar el contenedor
run_container() {
    echo -e "${BLUE}🚀 Ejecutando contenedor...${NC}"
    
    # Verificar si existe el archivo .env
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Archivo .env no encontrado. Copiando desde env.example...${NC}"
        cp ../env.example .env
        echo -e "${YELLOW}⚠️  Por favor, edita el archivo .env con tu API key de Gemini${NC}"
        exit 1
    fi
    
    # Detener contenedor si está ejecutándose
    docker stop ai-ticket-processor 2>/dev/null || true
    docker rm ai-ticket-processor 2>/dev/null || true
    
    # Ejecutar contenedor
    docker run -d \
        --name ai-ticket-processor \
        --env-file .env \
        -p 8003:8003 \
        -v "$(pwd)/images:/app/images:ro" \
        ai-ticket-processor
    
    echo -e "${GREEN}✅ Contenedor ejecutándose en http://localhost:8003${NC}"
    echo -e "${BLUE}📋 Para ver logs: $0 logs${NC}"
}

# Función para detener el contenedor
stop_container() {
    echo -e "${BLUE}🛑 Deteniendo contenedor...${NC}"
    docker stop ai-ticket-processor 2>/dev/null || true
    docker rm ai-ticket-processor 2>/dev/null || true
    echo -e "${GREEN}✅ Contenedor detenido${NC}"
}

# Función para reiniciar el contenedor
restart_container() {
    echo -e "${BLUE}🔄 Reiniciando contenedor...${NC}"
    stop_container
    run_container
}

# Función para mostrar logs
show_logs() {
    echo -e "${BLUE}📋 Mostrando logs del contenedor...${NC}"
    docker logs -f ai-ticket-processor
}

# Función para probar el servicio
test_service() {
    echo -e "${BLUE}🧪 Probando servicio...${NC}"
    
    # Esperar un momento para que el servicio se inicie
    sleep 3
    
    # Probar health check
    echo -e "${YELLOW}📡 Probando health check...${NC}"
    if curl -f http://localhost:8003/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check exitoso${NC}"
    else
        echo -e "${RED}❌ Health check falló${NC}"
        return 1
    fi
    
    # Probar información del modelo
    echo -e "${YELLOW}🤖 Probando información del modelo...${NC}"
    if curl -f http://localhost:8003/model-info >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Modelo funcionando correctamente${NC}"
    else
        echo -e "${RED}❌ Error obteniendo información del modelo${NC}"
        return 1
    fi
    
    echo -e "${GREEN}🎉 Servicio funcionando correctamente!${NC}"
    echo -e "${BLUE}📋 Endpoints disponibles:${NC}"
    echo -e "  - Health: http://localhost:8003/health"
    echo -e "  - Model Info: http://localhost:8003/model-info"
    echo -e "  - Process Ticket: http://localhost:8003/process-ticket"
}

# Función para limpiar
clean_docker() {
    echo -e "${BLUE}🧹 Limpiando Docker...${NC}"
    docker stop ai-ticket-processor 2>/dev/null || true
    docker rm ai-ticket-processor 2>/dev/null || true
    docker rmi ai-ticket-processor 2>/dev/null || true
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Manejo de comandos
case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    logs)
        show_logs
        ;;
    test)
        test_service
        ;;
    clean)
        clean_docker
        ;;
    help|*)
        show_help
        ;;
esac 