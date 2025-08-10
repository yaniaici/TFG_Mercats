#!/bin/bash

echo "🚀 Iniciando Ticket Service..."
echo "⏳ Esperando a que la base de datos esté lista..."
sleep 15

echo "🌱 Poblando tiendas del mercado..."
python seed_market_stores.py

echo "✅ Iniciando aplicación..."
exec uvicorn main:app --host 0.0.0.0 --port 8003 