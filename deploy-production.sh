#!/bin/bash

# Script de despliegue para producción
# Dominio: mercatmediterrani.com

echo "🚀 Desplegando Mercat Mediterrani en producción..."

# Variables de entorno para producción
export NODE_ENV=production
export REACT_APP_API_URL=https://mercatmediterrani.com

# 1. Parar servicios actuales
echo "📦 Parando servicios actuales..."
docker-compose down

# 2. Reconstruir imágenes con configuración de producción
echo "🔨 Reconstruyendo imágenes..."
docker-compose build --no-cache

# 3. Iniciar servicios
echo "🚀 Iniciando servicios..."
docker-compose up -d

# 4. Verificar salud de los servicios
echo "🏥 Verificando salud de los servicios..."
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
echo "🌐 Tu aplicación está disponible en: https://mercatmediterrani.com"
