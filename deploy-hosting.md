# 🚀 Guía de Despliegue para Servicios de Hosting

## 📋 Requisitos del Servidor

### **Requisitos Mínimos:**
- **CPU:** 2 cores
- **RAM:** 4GB mínimo, 8GB recomendado
- **Almacenamiento:** 20GB mínimo
- **Sistema Operativo:** Ubuntu 20.04+ o similar
- **Docker:** Versión 20.10+
- **Docker Compose:** Versión 2.0+

### **Puertos Necesarios:**
- **80/443:** Frontend (HTTP/HTTPS)
- **8000:** Backend API
- **8001:** Auth Service
- **8003:** Ticket Service
- **8004:** AI Ticket Processor
- **8005:** Gamification Service
- **8006:** CRM Service
- **8007:** Notification Service
- **5432:** PostgreSQL
- **11434:** Ollama (IA)

## 🔧 Configuración Inicial

### **1. Preparar el Servidor:**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

### **2. Configurar Variables de Entorno:**
```bash
# Crear archivo .env
cp .env.example .env

# Editar variables importantes:
nano .env
```

**Variables críticas a configurar:**
```env
# Base de datos
POSTGRES_DB=ticket_analytics
POSTGRES_USER=ticket_user
POSTGRES_PASSWORD=TU_PASSWORD_SEGURO

# JWT Secret
JWT_SECRET=TU_JWT_SECRET_MUY_SEGURO

# Dominio
DOMAIN=tu-dominio.com

# Puertos (opcional, por defecto usa los estándares)
FRONTEND_PORT=80
PGADMIN_PORT=8080

# Ollama Model
OLLAMA_MODEL=llama3.2:3b
```

### **3. Configurar Nginx (Recomendado):**
```bash
# Instalar Nginx
sudo apt install nginx -y

# Crear configuración
sudo nano /etc/nginx/sites-available/tu-dominio.com
```

**Contenido de la configuración:**
```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # APIs
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /auth/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /tickets/ {
        proxy_pass http://localhost:8003/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ai/ {
        proxy_pass http://localhost:8004/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /gamification/ {
        proxy_pass http://localhost:8005/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /crm/ {
        proxy_pass http://localhost:8006/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /notifications/ {
        proxy_pass http://localhost:8007/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/tu-dominio.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🚀 Despliegue

### **1. Subir Código al Servidor:**
```bash
# Clonar repositorio
git clone TU_REPOSITORIO
cd TFG

# O subir archivos via SCP/SFTP
scp -r . usuario@servidor:/ruta/del/proyecto
```

### **2. Construir y Ejecutar:**
```bash
# Construir imágenes
docker-compose build --no-cache

# Ejecutar servicios
docker-compose up -d

# Verificar estado
docker-compose ps
```

### **3. Configurar SSL (Opcional pero Recomendado):**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Renovar automáticamente
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 Verificación

### **1. Verificar Servicios:**
```bash
# Estado de contenedores
docker-compose ps

# Logs de servicios
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f auth-service
```

### **2. Verificar APIs:**
```bash
# Health checks
curl http://tu-dominio.com/api/health
curl http://tu-dominio.com/auth/health
curl http://tu-dominio.com/tickets/health
```

### **3. Verificar Base de Datos:**
```bash
# Acceder a pgAdmin
# URL: http://tu-dominio.com:8080
# Email: admin@example.com
# Password: (configurado en .env)
```

## 🛠️ Mantenimiento

### **Actualizaciones:**
```bash
# Parar servicios
docker-compose down

# Actualizar código
git pull

# Reconstruir y ejecutar
docker-compose build --no-cache
docker-compose up -d
```

### **Backups:**
```bash
# Backup de base de datos
docker-compose exec postgres pg_dump -U ticket_user ticket_analytics > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup de volúmenes
docker run --rm -v tfg_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### **Logs y Monitoreo:**
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f frontend

# Estadísticas de uso
docker stats
```

## 🚨 Solución de Problemas

### **Problemas Comunes:**

1. **Puertos ocupados:**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo lsof -i :80
   ```

2. **Permisos de Docker:**
   ```bash
   sudo chown $USER:$USER /var/run/docker.sock
   ```

3. **Espacio en disco:**
   ```bash
   docker system prune -a
   docker volume prune
   ```

4. **Servicios no inician:**
   ```bash
   docker-compose logs [servicio]
   docker-compose restart [servicio]
   ```

## 📞 Soporte

Para problemas específicos:
1. Revisar logs: `docker-compose logs [servicio]`
2. Verificar configuración: `docker-compose config`
3. Reiniciar servicios: `docker-compose restart`
4. Reconstruir: `docker-compose build --no-cache [servicio]`
