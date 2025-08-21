-- Script de verificación de recompensas
-- Script: 16_verify_rewards.sql

-- Verificar que la tabla rewards existe
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rewards') THEN
        RAISE NOTICE '✓ Tabla rewards creada correctamente';
    ELSE
        RAISE NOTICE '✗ ERROR: Tabla rewards no encontrada';
    END IF;
END $$;

-- Verificar que se insertaron las recompensas
DO $$
DECLARE
    reward_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO reward_count FROM rewards;
    
    IF reward_count > 0 THEN
        RAISE NOTICE '✓ Se insertaron % recompensas correctamente', reward_count;
        
        -- Mostrar algunas recompensas como ejemplo
        RAISE NOTICE 'Ejemplos de recompensas:';
        FOR r IN SELECT name, points_cost, reward_type FROM rewards LIMIT 5 LOOP
            RAISE NOTICE '  - % (% puntos, tipo: %)', r.name, r.points_cost, r.reward_type;
        END LOOP;
    ELSE
        RAISE NOTICE '✗ ERROR: No se encontraron recompensas en la tabla';
    END IF;
END $$;

-- Verificar tipos de recompensas
DO $$
BEGIN
    RAISE NOTICE 'Tipos de recompensas disponibles:';
    FOR t IN SELECT DISTINCT reward_type, COUNT(*) as count FROM rewards GROUP BY reward_type LOOP
        RAISE NOTICE '  - %: % recompensas', t.reward_type, t.count;
    END LOOP;
END $$;
