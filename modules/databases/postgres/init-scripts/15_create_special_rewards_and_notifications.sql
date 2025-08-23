-- Crear tablas para recompensas especiales y notificaciones personales
-- Script: 15_create_special_rewards_and_notifications.sql

-- Tabla de recompensas especiales (0 puntos)
CREATE TABLE IF NOT EXISTS special_rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500) NOT NULL,
    reward_type VARCHAR(100) NOT NULL,
    reward_value VARCHAR(255) NOT NULL,
    is_global BOOLEAN DEFAULT FALSE,
    target_users JSONB DEFAULT '[]',
    target_segments JSONB DEFAULT '[]',
    max_redemptions INTEGER,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de canjes de recompensas especiales
CREATE TABLE IF NOT EXISTS special_reward_redemptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    special_reward_id UUID NOT NULL REFERENCES special_rewards(id),
    redemption_code VARCHAR(50) NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de notificaciones personales del usuario
CREATE TABLE IF NOT EXISTS user_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_special_rewards_is_global ON special_rewards(is_global);
CREATE INDEX IF NOT EXISTS idx_special_rewards_is_active ON special_rewards(is_active);
CREATE INDEX IF NOT EXISTS idx_special_rewards_expires_at ON special_rewards(expires_at);
CREATE INDEX IF NOT EXISTS idx_special_reward_redemptions_user_id ON special_reward_redemptions(user_id);
CREATE INDEX IF NOT EXISTS idx_special_reward_redemptions_special_reward_id ON special_reward_redemptions(special_reward_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_is_read ON user_notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_user_notifications_created_at ON user_notifications(created_at);

-- Triggers para actualizar updated_at
CREATE TRIGGER update_special_rewards_updated_at 
    BEFORE UPDATE ON special_rewards 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_special_reward_redemptions_updated_at 
    BEFORE UPDATE ON special_reward_redemptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentarios para documentación
COMMENT ON TABLE special_rewards IS 'Tabla de recompensas especiales que no cuestan puntos';
COMMENT ON TABLE special_reward_redemptions IS 'Tabla de canjes de recompensas especiales realizados por usuarios';
COMMENT ON TABLE user_notifications IS 'Tabla de notificaciones personales de cada usuario';
COMMENT ON COLUMN special_rewards.is_global IS 'Si es TRUE, la recompensa está disponible para todos los usuarios';
COMMENT ON COLUMN special_rewards.target_users IS 'Array de user_ids específicos que pueden acceder a esta recompensa';
COMMENT ON COLUMN special_rewards.target_segments IS 'Array de segmentos que pueden acceder a esta recompensa';
COMMENT ON COLUMN special_rewards.max_redemptions IS 'Máximo número de canjes por usuario (NULL = ilimitado)';
COMMENT ON COLUMN user_notifications.notification_type IS 'Tipo: reward, special_reward, system, promotion';
COMMENT ON COLUMN user_notifications.related_id IS 'ID relacionado (reward_id, special_reward_id, etc.)';
COMMENT ON COLUMN user_notifications.read_at IS 'Fecha cuando se marcó como leída';

-- Insertar algunas recompensas especiales de ejemplo
INSERT INTO special_rewards (name, description, reward_type, reward_value, is_global, is_active) VALUES
('Benvinguda!', 'Recompensa especial per als nous usuaris', 'discount', '5% de descompte en la primera compra', true, true),
('Fidelitat', 'Recompensa per usuaris actius', 'parking', '1 hora de parking gratuït', false, true),
('Promoció d''estiu', 'Recompensa especial per l''estiu', 'food', 'Cafè gratuït', true, true)
ON CONFLICT DO NOTHING;

