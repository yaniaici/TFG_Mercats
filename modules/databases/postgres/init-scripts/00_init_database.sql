-- Script principal de inicialización de la base de datos
-- Este script ejecuta todos los scripts de inicialización en el orden correcto

-- Mensaje de inicio
DO $$
BEGIN
    RAISE NOTICE 'Iniciando inicialización de la base de datos TFG...';
END $$;

-- Los scripts se ejecutan automáticamente en orden alfabético por Docker
-- 01_create_extensions.sql - Extensiones necesarias
-- 02_create_main_tables.sql - Tablas principales
-- 03_create_auth_tables.sql - Tablas de autenticación
-- 04_create_triggers.sql - Triggers y funciones
-- 05_create_views.sql - Vistas del sistema
-- 06_create_purchase_history.sql - Tablas de historial de compras
-- 07_create_gamification_tables.sql - Tablas de gamificación
-- 08_create_rewards_tables.sql - Tablas de recompensas
-- 09_add_email_field.sql - Campos adicionales
-- 10_create_crm.sql - Tablas de CRM
-- 11_create_notification_sender_tables.sql - Tablas de notificaciones
-- 12_insert_initial_data.sql - Datos iniciales

-- Mensaje de finalización
DO $$
BEGIN
    RAISE NOTICE 'Inicialización de la base de datos TFG completada exitosamente';
    RAISE NOTICE 'Usuario administrador creado: admin@tfg.com / admin123';
    RAISE NOTICE 'IMPORTANTE: Cambiar la contraseña del administrador en producción';
END $$;
