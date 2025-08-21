-- Crear tablas para el sistema de recompensas
-- Script: 08_create_rewards_tables.sql

-- Tabla de recompensas disponibles
CREATE TABLE IF NOT EXISTS rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500) NOT NULL,
    points_cost INTEGER NOT NULL,
    reward_type VARCHAR(100) NOT NULL,
    reward_value VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_redemptions INTEGER,
    current_redemptions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de canjes de recompensas
CREATE TABLE IF NOT EXISTS reward_redemptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    reward_id UUID NOT NULL REFERENCES rewards(id),
    points_spent INTEGER NOT NULL,
    redemption_code VARCHAR(50) NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_rewards_active ON rewards(is_active);
CREATE INDEX IF NOT EXISTS idx_rewards_type ON rewards(reward_type);
CREATE INDEX IF NOT EXISTS idx_reward_redemptions_user_id ON reward_redemptions(user_id);
CREATE INDEX IF NOT EXISTS idx_reward_redemptions_reward_id ON reward_redemptions(reward_id);
CREATE INDEX IF NOT EXISTS idx_reward_redemptions_code ON reward_redemptions(redemption_code);
CREATE INDEX IF NOT EXISTS idx_reward_redemptions_used ON reward_redemptions(is_used);

-- Triggers para actualizar updated_at (usando la función ya definida en 04_create_triggers.sql)
CREATE TRIGGER update_rewards_updated_at 
    BEFORE UPDATE ON rewards 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reward_redemptions_updated_at 
    BEFORE UPDATE ON reward_redemptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentarios para documentación
COMMENT ON TABLE rewards IS 'Tabla de recompensas disponibles para canje';
COMMENT ON TABLE reward_redemptions IS 'Tabla de canjes de recompensas realizados por usuarios';
COMMENT ON COLUMN rewards.reward_type IS 'Tipo de recompensa: parking, discount, food, merchandise, experience';
COMMENT ON COLUMN rewards.reward_value IS 'Valor de la recompensa: ej: "1 hora", "10% descuento"';
COMMENT ON COLUMN reward_redemptions.redemption_code IS 'Código único para canjear la recompensa';
COMMENT ON COLUMN reward_redemptions.expires_at IS 'Fecha de expiración del canje (30 días por defecto)';
