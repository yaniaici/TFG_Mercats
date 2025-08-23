FROM postgres:15-alpine

# Variables de entorno para la base de datos
# Estas variables se sobrescriben desde docker-compose.yml
ENV POSTGRES_DB=tfg_db
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Los scripts de inicialización se montan como volumen desde docker-compose.yml
# No es necesario copiarlos aquí ya que se montan en /docker-entrypoint-initdb.d/

# Exponer puerto
EXPOSE 5432 