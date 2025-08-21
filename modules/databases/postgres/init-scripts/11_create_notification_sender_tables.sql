-- ========================================
-- TABLAS PARA NOTIFICATION SENDER
-- ========================================

-- Tabla para suscripciones de usuarios a diferentes canales
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('webpush', 'android', 'ios')),
    subscription_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para user_subscriptions
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_channel ON user_subscriptions(channel);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_active ON user_subscriptions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_channel ON user_subscriptions(user_id, channel);

-- Comentarios
COMMENT ON TABLE user_subscriptions IS 'Suscripciones de usuarios a diferentes canales de notificación';
COMMENT ON COLUMN user_subscriptions.user_id IS 'ID del usuario';
COMMENT ON COLUMN user_subscriptions.channel IS 'Canal de notificación (webpush, android, ios)';
COMMENT ON COLUMN user_subscriptions.subscription_data IS 'Datos específicos del canal (endpoint, keys, tokens, etc.)';
COMMENT ON COLUMN user_subscriptions.is_active IS 'Indica si la suscripción está activa';

-- Trigger para actualizar updated_at (usando la función ya definida)
CREATE TRIGGER trigger_update_user_subscriptions_updated_at
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Función para limpiar suscripciones inactivas (opcional)
CREATE OR REPLACE FUNCTION cleanup_inactive_subscriptions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_subscriptions 
    WHERE is_active = FALSE 
    AND updated_at < NOW() - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comentario sobre la función de limpieza
COMMENT ON FUNCTION cleanup_inactive_subscriptions() IS 'Limpia suscripciones inactivas de más de 30 días';

