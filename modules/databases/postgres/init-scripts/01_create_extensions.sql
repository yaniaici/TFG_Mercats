-- Script de inicialización: Extensiones necesarias
-- Este script se ejecuta automáticamente al crear el contenedor

-- Habilitar extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Habilitar extensión para funciones criptográficas (para hashing)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- JSONB ya está incluido en PostgreSQL core, no necesita extensión

-- Habilitar extensión para funciones de fecha/hora
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Crear función para obtener timestamp actual
CREATE OR REPLACE FUNCTION get_current_timestamp()
RETURNS TIMESTAMP WITH TIME ZONE AS $$
BEGIN
    RETURN NOW();
END;
$$ LANGUAGE plpgsql; 