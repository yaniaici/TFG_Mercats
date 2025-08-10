-- Script para añadir campos a la tabla users (email, role)
-- Este script se ejecuta automáticamente al crear el contenedor

-- Añadir columna email si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'email'
    ) THEN
        ALTER TABLE users ADD COLUMN email VARCHAR(255);
        
        -- Crear índice único para email si no existe
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_email'
            ) THEN
                CREATE UNIQUE INDEX idx_users_email ON users(email);
            END IF;
        END $$;
        
        -- Actualizar usuarios existentes para que email = email_hash
        UPDATE users SET email = email_hash WHERE email IS NULL;
        
        -- Hacer el campo email NOT NULL después de la migración
        ALTER TABLE users ALTER COLUMN email SET NOT NULL;
        
        RAISE NOTICE 'Campo email añadido a la tabla users';
    ELSE
        RAISE NOTICE 'Campo email ya existe en la tabla users';
    END IF;
END $$;

-- Añadir columna role si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user';
        
        -- Crear índice para role si no existe
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_role'
            ) THEN
                CREATE INDEX idx_users_role ON users(role);
            END IF;
        END $$;
        
        RAISE NOTICE 'Campo role añadido a la tabla users';
    ELSE
        RAISE NOTICE 'Campo role ya existe en la tabla users';
    END IF;
END $$;
