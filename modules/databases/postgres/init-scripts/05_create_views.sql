-- Script de inicialización: Creación de vistas útiles
-- Este script se ejecuta automáticamente al crear el contenedor

-- Vista para obtener información completa de usuarios con sus perfiles
CREATE OR REPLACE VIEW user_complete_info AS
SELECT 
    u.id,
    u.email_hash,
    u.registration_date,
    u.preferences,
    u.is_active,
    u.created_at,
    u.updated_at,
    up.user_type,
    up.segment,
    up.gamification_points,
    up.level
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id;

-- Vista para estadísticas de tickets por usuario
CREATE OR REPLACE VIEW user_ticket_stats AS
SELECT 
    u.id as user_id,
    u.email_hash,
    COUNT(t.id) as total_tickets,
    SUM(t.total_price) as total_spent,
    AVG(t.total_price) as avg_ticket_value,
    MIN(t.purchase_datetime) as first_purchase,
    MAX(t.purchase_datetime) as last_purchase,
    COUNT(CASE WHEN t.origin = 'escaneo' THEN 1 END) as scanned_tickets,
    COUNT(CASE WHEN t.origin = 'digital' THEN 1 END) as digital_tickets,
    COUNT(CASE WHEN t.origin = 'API' THEN 1 END) as api_tickets
FROM users u
LEFT JOIN tickets t ON u.id = t.user_id
GROUP BY u.id, u.email_hash;

-- Vista para tickets con información de usuario
CREATE OR REPLACE VIEW ticket_with_user AS
SELECT 
    t.id,
    t.user_id,
    u.email_hash,
    t.purchase_datetime,
    t.store_id,
    t.total_price,
    t.origin,
    t.processed,
    t.created_at,
    up.user_type,
    up.segment
FROM tickets t
LEFT JOIN users u ON t.user_id = u.id
LEFT JOIN user_profiles up ON u.id = up.user_id;

-- Vista para análisis de segmentos
CREATE OR REPLACE VIEW segment_analysis AS
SELECT 
    up.segment,
    COUNT(DISTINCT u.id) as user_count,
    COUNT(t.id) as total_tickets,
    SUM(t.total_price) as total_revenue,
    AVG(t.total_price) as avg_ticket_value,
    AVG(up.gamification_points) as avg_gamification_points,
    AVG(up.level) as avg_level
FROM user_profiles up
JOIN users u ON up.user_id = u.id
LEFT JOIN tickets t ON u.id = t.user_id
WHERE up.segment IS NOT NULL
GROUP BY up.segment;

-- Vista para tickets no procesados (pendientes de IA)
CREATE OR REPLACE VIEW pending_tickets AS
SELECT 
    t.id,
    t.user_id,
    t.purchase_datetime,
    t.store_id,
    t.total_price,
    t.origin,
    t.created_at,
    ti.image_path,
    ti.image_hash
FROM tickets t
LEFT JOIN ticket_images ti ON t.id = ti.ticket_id
WHERE t.processed = FALSE
ORDER BY t.created_at ASC;

-- Vista para auditoría reciente
CREATE OR REPLACE VIEW recent_audit_logs AS
SELECT 
    al.id,
    al.table_name,
    al.record_id,
    al.action,
    al.old_values,
    al.new_values,
    al.user_id,
    al.created_at,
    u.email_hash
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.id
ORDER BY al.created_at DESC
LIMIT 1000; 