-- Crear tablas para el sistema de gamificación

-- Tabla de perfil de gamificación del usuario
CREATE TABLE IF NOT EXISTS user_gamification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    total_tickets INTEGER DEFAULT 0,
    valid_tickets INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.0,
    streak_days INTEGER DEFAULT 0,
    last_scan_date TIMESTAMP WITH TIME ZONE,
    badges_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de insignias de usuario
CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    badge_type VARCHAR(100) NOT NULL,
    badge_name VARCHAR(255) NOT NULL,
    badge_description VARCHAR(500) NOT NULL,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabla de log de experiencia
CREATE TABLE IF NOT EXISTS experience_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    ticket_id UUID,
    experience_gained INTEGER NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_user_gamification_user_id ON user_gamification(user_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_type ON user_badges(badge_type);
CREATE INDEX IF NOT EXISTS idx_experience_log_user_id ON experience_log(user_id);
CREATE INDEX IF NOT EXISTS idx_experience_log_created_at ON experience_log(created_at);

-- Trigger para actualizar updated_at en user_gamification (usando la función ya definida)
CREATE TRIGGER trigger_update_user_gamification_updated_at
    BEFORE UPDATE ON user_gamification
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insertar comentarios en las tablas
COMMENT ON TABLE user_gamification IS 'Perfil de gamificación de cada usuario';
COMMENT ON TABLE user_badges IS 'Insignias ganadas por los usuarios';
COMMENT ON TABLE experience_log IS 'Historial de experiencia ganada por los usuarios'; 