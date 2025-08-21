#!/bin/bash

# Script de despliegue para el servidor 95.63.163.200
# Dominio: mercatmediterrani.com

echo "🚀 Desplegando Mercat Mediterrani en el servidor..."

# Variables de entorno para producción
export NODE_ENV=production
export REACT_APP_API_URL=https://mercatmediterrani.com

# 1. Instalar dependencias del sistema
echo "📦 Instalando dependencias del sistema..."
sudo apt update
sudo apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx

# 2. Iniciar Docker
echo "🐳 Iniciando Docker..."
sudo systemctl start docker
sudo systemctl enable docker

# 3. Parar servicios actuales
echo "🛑 Parando servicios actuales..."
docker-compose down

# 4. Reconstruir imágenes
echo "🔨 Reconstruyendo imágenes..."
docker-compose build --no-cache

# 5. Iniciar servicios
echo "🚀 Iniciando servicios..."
docker-compose up -d

# 6. Configurar Nginx
echo "🌐 Configurando Nginx..."
sudo cp nginx-server.conf /etc/nginx/sites-available/mercatmediterrani.com
sudo ln -sf /etc/nginx/sites-available/mercatmediterrani.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 7. Configurar firewall
echo "🔥 Configurando firewall..."
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw --force enable

# 8. Verificar servicios
echo "🏥 Verificando servicios..."
sleep 30

# Verificar frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend funcionando correctamente"
else
    echo "❌ Error en el frontend"
fi

# Verificar backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend funcionando correctamente"
else
    echo "❌ Error en el backend"
fi

# Verificar auth service
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Auth service funcionando correctamente"
else
    echo "❌ Error en auth service"
fi

# Verificar ticket service
if curl -f http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ Ticket service funcionando correctamente"
else
    echo "❌ Error en ticket service"
fi

echo "🎉 Despliegue completado!"
echo "🌐 Tu aplicación está disponible en:"
echo "   • http://mercatmediterrani.com"
echo "   • http://95.63.163.200:3000"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configurar DNS del dominio para apuntar a 95.63.163.200"
echo "2. Obtener certificado SSL: sudo certbot --nginx -d mercatmediterrani.com"
echo "3. Reiniciar Nginx: sudo systemctl restart nginx"
