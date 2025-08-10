FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias de Python
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Hacer el script de migración ejecutable
RUN chmod +x /app/fix_user_emails.py

# Exponer puerto
EXPOSE 8001

# Comando para ejecutar la aplicación con migración
CMD ["sh", "-c", "python fix_user_emails.py && uvicorn main:app --host 0.0.0.0 --port 8001"] 