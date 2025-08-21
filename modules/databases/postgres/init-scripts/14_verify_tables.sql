-- Script de verificación: Comprobar que todas las tablas se han creado correctamente
-- Este script se ejecuta al final de la inicialización

DO $$
DECLARE
    expected_tables TEXT[] := ARRAY[
        'users', 'user_profiles', 'vendors', 'stores', 'tickets', 'ticket_images', 
        'ticket_attachments', 'ticket_comments', 'audit_logs', 'user_sessions', 
        'password_resets', 'email_verifications', 'failed_login_attempts', 
        'user_activity_logs', 'roles', 'permissions', 'role_permissions', 'user_roles',
        'purchase_history', 'user_gamification', 'user_badges', 'experience_log',
        'rewards', 'reward_redemptions', 'segments', 'campaigns', 'campaign_segments',
        'notifications', 'user_subscriptions', 'market_stores', 'ticket_files'
    ];
    table_name TEXT;
    table_exists BOOLEAN;
    missing_tables TEXT[] := ARRAY[]::TEXT[];
BEGIN
    RAISE NOTICE 'Verificando que todas las tablas se han creado correctamente...';
    
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
        RAISE NOTICE 'VERIFICACIÓN EXITOSA: Todas las tablas se han creado correctamente';
    ELSE
        RAISE NOTICE 'ERROR: Faltan las siguientes tablas: %', array_to_string(missing_tables, ', ');
    END IF;
    
    -- Verificar extensiones
    RAISE NOTICE 'Verificando extensiones...';
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp') THEN
        RAISE NOTICE 'OK: Extensión uuid-ossp instalada';
    ELSE
        RAISE NOTICE 'ERROR: Extensión uuid-ossp no encontrada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
        RAISE NOTICE 'OK: Extensión pgcrypto instalada';
    ELSE
        RAISE NOTICE 'ERROR: Extensión pgcrypto no encontrada';
    END IF;
    
    -- Verificar funciones
    RAISE NOTICE 'Verificando funciones...';
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_current_timestamp') THEN
        RAISE NOTICE 'OK: Función get_current_timestamp creada';
    ELSE
        RAISE NOTICE 'ERROR: Función get_current_timestamp no encontrada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
        RAISE NOTICE 'OK: Función update_updated_at_column creada';
    ELSE
        RAISE NOTICE 'ERROR: Función update_updated_at_column no encontrada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'audit_trigger_function') THEN
        RAISE NOTICE 'OK: Función audit_trigger_function creada';
    ELSE
        RAISE NOTICE 'ERROR: Función audit_trigger_function no encontrada';
    END IF;
    
    -- Verificar campos críticos en tablas principales
    RAISE NOTICE 'Verificando campos críticos...';
    
    -- Verificar tabla users
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'email') THEN
        RAISE NOTICE 'OK: Campo email en tabla users';
    ELSE
        RAISE NOTICE 'ERROR: Campo email no encontrado en tabla users';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'email_hash') THEN
        RAISE NOTICE 'OK: Campo email_hash en tabla users';
    ELSE
        RAISE NOTICE 'ERROR: Campo email_hash no encontrado en tabla users';
    END IF;
    
    -- Verificar tabla tickets
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tickets' AND column_name = 'purchase_datetime') THEN
        RAISE NOTICE 'OK: Campo purchase_datetime en tabla tickets';
    ELSE
        RAISE NOTICE 'ERROR: Campo purchase_datetime no encontrado en tabla tickets';
    END IF;
    
    RAISE NOTICE 'Verificación completada';
END $$;
