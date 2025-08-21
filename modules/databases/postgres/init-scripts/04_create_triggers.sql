-- Script de inicialización: Creación de triggers para auditoría y timestamps
-- Este script se ejecuta automáticamente al crear el contenedor

-- Función para actualizar el campo updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = get_current_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Función para crear logs de auditoría automáticamente
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_values, user_id)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW), 
                CASE 
                    WHEN TG_TABLE_NAME = 'users' THEN NEW.id
                    WHEN TG_TABLE_NAME = 'user_profiles' THEN NEW.user_id
                    WHEN TG_TABLE_NAME = 'tickets' THEN NEW.user_id
                    WHEN TG_TABLE_NAME = 'ticket_images' THEN 
                        (SELECT user_id FROM tickets WHERE id = NEW.ticket_id)
                    ELSE NULL
                END);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, user_id)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), 
                CASE 
                    WHEN TG_TABLE_NAME = 'users' THEN NEW.id
                    WHEN TG_TABLE_NAME = 'user_profiles' THEN NEW.user_id
                    WHEN TG_TABLE_NAME = 'tickets' THEN NEW.user_id
                    WHEN TG_TABLE_NAME = 'ticket_images' THEN 
                        (SELECT user_id FROM tickets WHERE id = NEW.ticket_id)
                    ELSE NULL
                END);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, user_id)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD), 
                CASE 
                    WHEN TG_TABLE_NAME = 'users' THEN OLD.id
                    WHEN TG_TABLE_NAME = 'user_profiles' THEN OLD.user_id
                    WHEN TG_TABLE_NAME = 'tickets' THEN OLD.user_id
                    WHEN TG_TABLE_NAME = 'ticket_images' THEN 
                        (SELECT user_id FROM tickets WHERE id = OLD.ticket_id)
                    ELSE NULL
                END);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Función para limpiar imágenes expiradas automáticamente
CREATE OR REPLACE FUNCTION cleanup_expired_images()
RETURNS TRIGGER AS $$
BEGIN
    -- Eliminar imágenes que han expirado
    DELETE FROM ticket_images 
    WHERE expires_at < get_current_timestamp();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vendors_updated_at
    BEFORE UPDATE ON vendors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stores_updated_at
    BEFORE UPDATE ON stores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Triggers para auditoría (solo en tablas principales)
-- Comentado temporalmente para evitar errores durante la inicialización
-- CREATE TRIGGER audit_users_trigger
--     AFTER INSERT OR UPDATE OR DELETE ON users
--     FOR EACH ROW
--     EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_user_profiles_trigger
    AFTER INSERT OR UPDATE OR DELETE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_tickets_trigger
    AFTER INSERT OR UPDATE OR DELETE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_ticket_images_trigger
    AFTER INSERT OR UPDATE OR DELETE ON ticket_images
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- Trigger para limpiar imágenes expiradas (se ejecuta cada vez que se inserta una nueva imagen)
CREATE TRIGGER cleanup_expired_images_trigger
    AFTER INSERT ON ticket_images
    FOR EACH ROW
    EXECUTE FUNCTION cleanup_expired_images(); 