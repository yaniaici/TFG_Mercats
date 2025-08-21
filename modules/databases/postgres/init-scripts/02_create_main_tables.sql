-- Script de inicialización: Tablas principales del sistema
-- Este script se ejecuta automáticamente al crear el contenedor

-- Tabla de usuarios (compatible con todos los servicios)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    email_hash VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Tabla de perfiles de usuario
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user_type VARCHAR(50) DEFAULT 'regular',
    segment VARCHAR(100),
    gamification_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Tabla de vendedores
CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    business_description TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Tabla de tiendas
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Tabla de tickets (versión unificada)
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    store_id VARCHAR(100) NOT NULL,
    purchase_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    origin VARCHAR(50) NOT NULL DEFAULT 'escaneo',
    ticket_hash VARCHAR(255),
    processed BOOLEAN DEFAULT FALSE,
    title VARCHAR(255),
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'resolved', 'cancelled')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    category VARCHAR(100),
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    estimated_resolution_time TIMESTAMP WITH TIME ZONE
);

-- Tabla de imágenes de tickets
CREATE TABLE IF NOT EXISTS ticket_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    image_path VARCHAR(500) NOT NULL,
    image_hash VARCHAR(255) NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (get_current_timestamp() + INTERVAL '24 hours')
);

-- Tabla de archivos adjuntos (para compatibilidad)
CREATE TABLE IF NOT EXISTS ticket_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Tabla de comentarios de tickets
CREATE TABLE IF NOT EXISTS ticket_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Tabla de logs de auditoría
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT get_current_timestamp()
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_email_hash ON users(email_hash);
CREATE INDEX IF NOT EXISTS idx_users_registration_date ON users(registration_date);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_type ON user_profiles(user_type);
CREATE INDEX IF NOT EXISTS idx_user_profiles_segment ON user_profiles(segment);
CREATE INDEX IF NOT EXISTS idx_user_profiles_gamification_points ON user_profiles(gamification_points);
CREATE INDEX IF NOT EXISTS idx_user_profiles_level ON user_profiles(level);

CREATE INDEX IF NOT EXISTS idx_vendors_user_id ON vendors(user_id);
CREATE INDEX IF NOT EXISTS idx_stores_vendor_id ON stores(vendor_id);

CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_store_id ON tickets(store_id);
CREATE INDEX IF NOT EXISTS idx_tickets_purchase_datetime ON tickets(purchase_datetime);
CREATE INDEX IF NOT EXISTS idx_tickets_origin ON tickets(origin);
CREATE INDEX IF NOT EXISTS idx_tickets_processed ON tickets(processed);
CREATE INDEX IF NOT EXISTS idx_tickets_ticket_hash ON tickets(ticket_hash);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_user_date ON tickets(user_id, purchase_datetime);

CREATE INDEX IF NOT EXISTS idx_ticket_images_ticket_id ON ticket_images(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_images_processed ON ticket_images(processed);
CREATE INDEX IF NOT EXISTS idx_ticket_images_expires_at ON ticket_images(expires_at);
CREATE INDEX IF NOT EXISTS idx_ticket_images_image_hash ON ticket_images(image_hash);

CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket_id ON ticket_comments(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_attachments_ticket_id ON ticket_attachments(ticket_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_table_name ON audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_record_id ON audit_logs(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_record ON audit_logs(table_name, record_id, created_at);
