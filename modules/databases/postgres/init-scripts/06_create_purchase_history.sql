-- Crear tabla de historial de compras
CREATE TABLE IF NOT EXISTS purchase_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    ticket_id UUID NOT NULL,
    purchase_date TIMESTAMP WITH TIME ZONE NOT NULL,
    store_name VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    products JSONB DEFAULT '[]',
    num_products INTEGER DEFAULT 0,
    ticket_type VARCHAR(100),
    is_market_store BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_purchase_history_user_id ON purchase_history(user_id);
CREATE INDEX IF NOT EXISTS idx_purchase_history_ticket_id ON purchase_history(ticket_id);
CREATE INDEX IF NOT EXISTS idx_purchase_history_purchase_date ON purchase_history(purchase_date);
CREATE INDEX IF NOT EXISTS idx_purchase_history_store_name ON purchase_history(store_name);

-- Crear índice compuesto para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_purchase_history_user_date ON purchase_history(user_id, purchase_date DESC);

-- Añadir comentarios a la tabla
COMMENT ON TABLE purchase_history IS 'Historial de compras de los usuarios basado en tickets procesados';
COMMENT ON COLUMN purchase_history.user_id IS 'ID del usuario que realizó la compra';
COMMENT ON COLUMN purchase_history.ticket_id IS 'ID del ticket procesado';
COMMENT ON COLUMN purchase_history.purchase_date IS 'Fecha de la compra';
COMMENT ON COLUMN purchase_history.store_name IS 'Nombre de la tienda donde se realizó la compra';
COMMENT ON COLUMN purchase_history.total_amount IS 'Total de la compra en euros';
COMMENT ON COLUMN purchase_history.products IS 'Lista de productos comprados en formato JSON';
COMMENT ON COLUMN purchase_history.num_products IS 'Número total de productos';
COMMENT ON COLUMN purchase_history.ticket_type IS 'Tipo de ticket (compra, devolución, etc.)';
COMMENT ON COLUMN purchase_history.is_market_store IS 'Indica si la tienda es del mercado';

-- Trigger para actualizar updated_at automáticamente (usando la función ya definida)
CREATE TRIGGER trigger_update_purchase_history_updated_at
    BEFORE UPDATE ON purchase_history
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 