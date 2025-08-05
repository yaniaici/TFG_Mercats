FROM postgres:15-alpine

# Variables de entorno para la base de datos
ENV POSTGRES_DB=ticket_analytics
ENV POSTGRES_USER=ticket_user
ENV POSTGRES_PASSWORD=ticket_password

# Copiar scripts de inicialización
COPY init-scripts/ /docker-entrypoint-initdb.d/

# Exponer puerto
EXPOSE 5432

# Configuraciones adicionales de PostgreSQL
COPY postgresql.conf /var/lib/postgresql/data/postgresql.conf

CMD ["postgres", "-c", "config_file=/var/lib/postgresql/data/postgresql.conf"] 