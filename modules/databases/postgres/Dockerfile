FROM postgres:15-alpine

# Variables de entorno para la base de datos
# Estas variables se sobrescriben desde docker-compose.yml
ENV POSTGRES_DB=tfg_db
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Copiar scripts de inicialización
COPY init-scripts/ /docker-entrypoint-initdb.d/

# Exponer puerto
EXPOSE 5432 