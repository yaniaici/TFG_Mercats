#!/bin/bash

# 🚀 Script de Despliegue para Hosting
# Uso: ./deploy-hosting.sh [DOMINIO]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si se proporcionó un dominio
if [ -z "$1" ]; then
    print_error "Uso: $0 <dominio>"
    print_error "Ejemplo: $0 mi-dominio.com"
    exit 1
fi

DOMAIN=$1
print_status "Iniciando despliegue para dominio: $DOMAIN"

# Verificar si estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    print_error "No se encontró docker-compose.yml. Ejecuta este script desde el directorio raíz del proyecto."
    exit 1
fi

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_success "Docker instalado. Por favor, reinicia la sesión y ejecuta el script nuevamente."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose instalado."
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    print_status "Creando archivo .env..."
    cat > .env << EOF
# Configuración de Base de Datos
POSTGRES_DB=ticket_analytics
POSTGRES_USER=ticket_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# JWT Secret
JWT_SECRET=$(openssl rand -base64 64)

# Dominio
DOMAIN=$DOMAIN

# Puertos
FRONTEND_PORT=3000
PGADMIN_PORT=8080

# Ollama Model
OLLAMA_MODEL=llama3.2:3b

# PgAdmin
PGADMIN_DEFAULT_EMAIL=admin@$DOMAIN
PGADMIN_DEFAULT_PASSWORD=$(openssl rand -base64 16)

# VAPID Keys (para notificaciones push)
VAPID_PRIVATE_KEY=$(openssl ecparam -genkey -name prime256v1 -noout -outform pem | base64 -w 0)
VAPID_PUBLIC_KEY=$(openssl ec -in <(echo "$VAPID_PRIVATE_KEY" | base64 -d) -pubout -outform pem | base64 -w 0)

# Habilitar detección de duplicados
ENABLE_DUPLICATE_DETECTION=true
EOF
    print_success "Archivo .env creado con configuración segura."
else
    print_warning "El archivo .env ya existe. Verifica que las variables estén configuradas correctamente."
fi

# Parar servicios existentes
print_status "Parando servicios existentes..."
docker-compose down 2>/dev/null || true

# Limpiar imágenes antiguas
print_status "Limpiando imágenes antiguas..."
docker system prune -f

# Construir imágenes
print_status "Construyendo imágenes Docker..."
docker-compose build --no-cache

# Ejecutar servicios
print_status "Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
print_status "Esperando a que los servicios estén listos..."
sleep 30

# Verificar estado de los servicios
print_status "Verificando estado de los servicios..."
docker-compose ps

# Verificar health checks
print_status "Verificando health checks..."
for service in backend auth-service ticket-service; do
    if docker-compose ps $service | grep -q "healthy"; then
        print_success "$service está funcionando correctamente."
    else
        print_warning "$service puede tener problemas. Revisa los logs con: docker-compose logs $service"
    fi
done

# Configurar Nginx si está disponible
if command -v nginx &> /dev/null; then
    print_status "Configurando Nginx..."
    
    # Crear configuración de Nginx
    sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # APIs
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /auth/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /tickets/ {
        proxy_pass http://localhost:8003/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /ai/ {
        proxy_pass http://localhost:8004/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /gamification/ {
        proxy_pass http://localhost:8005/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /crm/ {
        proxy_pass http://localhost:8006/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /notifications/ {
        proxy_pass http://localhost:8007/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Activar sitio
    sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    
    print_success "Nginx configurado para $DOMAIN"
else
    print_warning "Nginx no está instalado. Instala Nginx para mejor rendimiento:"
    print_warning "sudo apt install nginx -y"
fi

# Mostrar información final
print_success "¡Despliegue completado!"
echo ""
echo "📋 Información del despliegue:"
echo "   🌐 Frontend: http://$DOMAIN"
echo "   🔧 Backend API: http://$DOMAIN/api"
echo "   🔐 Auth Service: http://$DOMAIN/auth"
echo "   🎫 Ticket Service: http://$DOMAIN/tickets"
echo "   🤖 AI Service: http://$DOMAIN/ai"
echo "   🏆 Gamification: http://$DOMAIN/gamification"
echo "   👥 CRM Service: http://$DOMAIN/crm"
echo "   📢 Notifications: http://$DOMAIN/notifications"
echo "   🗄️  PgAdmin: http://$DOMAIN:8080"
echo ""
echo "🔑 Credenciales PgAdmin:"
echo "   Email: admin@$DOMAIN"
echo "   Password: $(grep PGADMIN_DEFAULT_PASSWORD .env | cut -d'=' -f2)"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Reiniciar: docker-compose restart"
echo "   Parar: docker-compose down"
echo "   Estado: docker-compose ps"
echo ""
print_warning "Recuerda configurar los registros DNS para que $DOMAIN apunte a este servidor."
