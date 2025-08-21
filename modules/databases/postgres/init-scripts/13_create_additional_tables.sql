-- Script de inicialización: Tablas adicionales del sistema
-- Este script se ejecuta automáticamente al crear el contenedor

-- Tabla de tiendas del mercado (para el ticket-service)
CREATE TABLE IF NOT EXISTS market_stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Tabla de archivos de tickets (para el ticket-service)
CREATE TABLE IF NOT EXISTS ticket_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    ticket_metadata JSONB DEFAULT '{}',
    processing_result JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Índices para las nuevas tablas
CREATE INDEX IF NOT EXISTS idx_market_stores_name ON market_stores(name);
CREATE INDEX IF NOT EXISTS idx_market_stores_is_active ON market_stores(is_active);

CREATE INDEX IF NOT EXISTS idx_ticket_files_user_id ON ticket_files(user_id);
CREATE INDEX IF NOT EXISTS idx_ticket_files_status ON ticket_files(status);
CREATE INDEX IF NOT EXISTS idx_ticket_files_created_at ON ticket_files(created_at);

-- Triggers para actualizar updated_at
CREATE TRIGGER update_market_stores_updated_at
    BEFORE UPDATE ON market_stores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ticket_files_updated_at
    BEFORE UPDATE ON ticket_files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comentarios
COMMENT ON TABLE market_stores IS 'Tiendas del mercado disponibles para tickets';
COMMENT ON TABLE ticket_files IS 'Archivos de tickets subidos por usuarios';
