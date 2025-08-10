#!/usr/bin/env python3
"""
Script para migrar usuarios existentes y añadir el campo email real
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, engine
from models import User
from sqlalchemy.orm import Session
from sqlalchemy import text

def fix_user_emails():
    """Migra usuarios existentes para añadir el campo email"""
    
    db = next(get_db())
    
    try:
        # Migración: consolidar a una sola columna email y eliminar email_hash
        print("🔧 Ejecutando migración SQL de consolidación de email...")
        
        # Verificar si el campo email existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'email'
        """))
        
        if not result.fetchone():
            db.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
            print("📝 Columna email creada")
        # Rellenar email a partir de email_hash si existe la columna; si no, omitir
        db.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='email_hash'
            ) THEN
                UPDATE users SET email = email_hash WHERE email IS NULL OR email = '';
            END IF;
        END $$;
        """))
        # Asegurar unicidad: crear índice único si no existe
        db.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_email') THEN CREATE UNIQUE INDEX idx_users_email ON users(email); END IF; END $$;"))
        # Marcar NOT NULL
        db.execute(text("ALTER TABLE users ALTER COLUMN email SET NOT NULL"))
        # Eliminar columna email_hash si existe (ignorar errores si no existe)
        db.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='email_hash'
            ) THEN
                BEGIN
                    ALTER TABLE users DROP COLUMN email_hash;
                EXCEPTION WHEN undefined_column THEN
                    -- Ignorar si no existe
                    NULL;
                END;
            END IF;
        END $$;
        """))
        print("✅ Consolidación completada: solo 'email'")
        
        db.commit()
        
        # Verificar que todos los usuarios tengan email
        print("🔍 Verificando usuarios sin email...")
        
        # Usar SQL directo para evitar problemas con SQLAlchemy
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE email IS NULL"))
        users_without_email = result.fetchone()[0]
        
        if users_without_email > 0:
            print(f"⚠️ Encontrados {users_without_email} usuarios sin email, actualizando...")
            
            # Intentar actualizar usuarios sin email desde email_hash si existe; si no, dejar como está
            db.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='email_hash'
                ) THEN
                    UPDATE users SET email = email_hash WHERE email IS NULL;
                END IF;
            END $$;
            """))
            db.commit()
            
            print(f"✅ {users_without_email} usuarios actualizados")
        else:
            print("✅ Todos los usuarios tienen email")
        
        # Mostrar estadísticas finales
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        total_users = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE email IS NOT NULL"))
        users_with_email = result.fetchone()[0]
        
        print(f"\n📊 Estadísticas finales:")
        print(f"   Total de usuarios: {total_users}")
        print(f"   Usuarios con email: {users_with_email}")
        print(f"   Usuarios sin email: {total_users - users_with_email}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error en la migración: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_user_emails()
