-- Script principal de inicialización de la base de datos
-- Este script ejecuta todos los scripts de inicialización en el orden correcto

-- Mensaje de inicio
DO $$
BEGIN
    RAISE NOTICE 'Iniciando inicialización de la base de datos TFG...';
END $$;

-- Los scripts se ejecutan automáticamente en orden alfabético por Docker
-- 01_create_extensions.sql - Extensiones necesarias (uuid-ossp, pgcrypto, etc.)
-- 02_create_main_tables.sql - Tablas principales (users, user_profiles, vendors, stores, tickets, ticket_images, audit_logs)
-- 03_create_auth_tables.sql - Tablas de autenticación (sessions, roles, permissions, etc.)
-- 04_create_triggers.sql - Triggers y funciones (updated_at, auditoría, limpieza)
-- 05_create_views.sql - Vistas del sistema (user_complete_info, ticket_stats, etc.)
-- 06_create_purchase_history.sql - Tabla de historial de compras
-- 07_create_gamification_tables.sql - Tablas de gamificación (user_gamification, badges, experience)
-- 08_create_rewards_tables.sql - Tablas de recompensas (rewards, redemptions)
-- 10_create_crm.sql - Tablas de CRM (segments, campaigns, notifications)
-- 11_create_notification_sender_tables.sql - Tablas de notificaciones (user_subscriptions)
-- 12_insert_initial_data.sql - Datos iniciales (roles, permissions, admin user)
-- 13_create_additional_tables.sql - Tablas adicionales (market_stores, ticket_files)

-- Mensaje de finalización
DO $$
BEGIN
    RAISE NOTICE 'Inicialización de la base de datos TFG completada exitosamente';
    RAISE NOTICE 'Usuario administrador creado: admin@tfg.com / admin123';
    RAISE NOTICE 'IMPORTANTE: Cambiar la contraseña del administrador en producción';
    RAISE NOTICE 'Tablas creadas: users, user_profiles, vendors, stores, tickets, ticket_images, audit_logs, roles, permissions, purchase_history, user_gamification, rewards, segments, campaigns, notifications, user_subscriptions, market_stores, ticket_files';
END $$;
