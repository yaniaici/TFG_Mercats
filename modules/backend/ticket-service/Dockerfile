FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio de uploads
RUN mkdir -p uploads

# Hacer el script ejecutable
RUN chmod +x /app/init.sh

# Exponer puerto
EXPOSE 8003

# Comando para ejecutar la aplicación con inicialización
CMD ["/app/init.sh"] 