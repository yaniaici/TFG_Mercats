-- Script de verificación: Comprobar que las tablas de recompensas especiales y notificaciones se han creado correctamente
-- Este script se ejecuta después de crear las nuevas tablas

DO $$
DECLARE
    expected_tables TEXT[] := ARRAY[
        'special_rewards', 'special_reward_redemptions', 'user_notifications'
    ];
    table_name TEXT;
    table_exists BOOLEAN;
    missing_tables TEXT[] := ARRAY[]::TEXT[];
BEGIN
    RAISE NOTICE 'Verificando que las tablas de recompensas especiales y notificaciones se han creado correctamente...';
    
    -- Verificar cada tabla esperada
    FOREACH table_name IN ARRAY expected_tables
    LOOP
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = table_name
        ) INTO table_exists;
        
        IF NOT table_exists THEN
            missing_tables := array_append(missing_tables, table_name);
            RAISE NOTICE 'ERROR: Tabla % no encontrada', table_name;
        ELSE
            RAISE NOTICE 'OK: Tabla % creada correctamente', table_name;
        END IF;
    END LOOP;
    
    -- Reporte final
    IF array_length(missing_tables, 1) IS NULL THEN
        RAISE NOTICE 'VERIFICACIÓN EXITOSA: Todas las tablas de recompensas especiales se han creado correctamente';
    ELSE
        RAISE NOTICE 'ERROR: Faltan las siguientes tablas: %', array_to_string(missing_tables, ', ');
    END IF;
    
    -- Verificar campos críticos en tablas principales
    RAISE NOTICE 'Verificando campos críticos...';
    
    -- Verificar tabla special_rewards
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'special_rewards' AND column_name = 'is_global') THEN
        RAISE NOTICE 'OK: Campo is_global en tabla special_rewards';
    ELSE
        RAISE NOTICE 'ERROR: Campo is_global no encontrado en tabla special_rewards';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'special_rewards' AND column_name = 'target_users') THEN
        RAISE NOTICE 'OK: Campo target_users en tabla special_rewards';
    ELSE
        RAISE NOTICE 'ERROR: Campo target_users no encontrado en tabla special_rewards';
    END IF;
    
    -- Verificar tabla special_reward_redemptions
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'special_reward_redemptions' AND column_name = 'redemption_code') THEN
        RAISE NOTICE 'OK: Campo redemption_code en tabla special_reward_redemptions';
    ELSE
        RAISE NOTICE 'ERROR: Campo redemption_code no encontrado en tabla special_reward_redemptions';
    END IF;
    
    -- Verificar tabla user_notifications
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_notifications' AND column_name = 'is_read') THEN
        RAISE NOTICE 'OK: Campo is_read en tabla user_notifications';
    ELSE
        RAISE NOTICE 'ERROR: Campo is_read no encontrado en tabla user_notifications';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_notifications' AND column_name = 'notification_type') THEN
        RAISE NOTICE 'OK: Campo notification_type en tabla user_notifications';
    ELSE
        RAISE NOTICE 'ERROR: Campo notification_type no encontrado en tabla user_notifications';
    END IF;
    
    -- Verificar índices
    RAISE NOTICE 'Verificando índices...';
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_special_rewards_is_global') THEN
        RAISE NOTICE 'OK: Índice idx_special_rewards_is_global creado';
    ELSE
        RAISE NOTICE 'ERROR: Índice idx_special_rewards_is_global no encontrado';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_notifications_user_id') THEN
        RAISE NOTICE 'OK: Índice idx_user_notifications_user_id creado';
    ELSE
        RAISE NOTICE 'ERROR: Índice idx_user_notifications_user_id no encontrado';
    END IF;
    
    -- Verificar datos de ejemplo
    RAISE NOTICE 'Verificando datos de ejemplo...';
    
    IF EXISTS (SELECT 1 FROM special_rewards WHERE name = 'Benvinguda!') THEN
        RAISE NOTICE 'OK: Recompensa de ejemplo "Benvinguda!" insertada';
    ELSE
        RAISE NOTICE 'WARNING: Recompensa de ejemplo "Benvinguda!" no encontrada';
    END IF;
    
    RAISE NOTICE 'Verificación de recompensas especiales completada';
END $$;

