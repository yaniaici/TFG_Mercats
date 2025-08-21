-- Script de inicialización: Datos iniciales del sistema
-- Este script se ejecuta automáticamente al crear el contenedor

-- Insertar roles básicos
INSERT INTO roles (name, description) VALUES
    ('admin', 'Administrador del sistema con acceso completo'),
    ('vendor', 'Vendedor con acceso a gestión de tiendas y tickets'),
    ('user', 'Usuario regular con acceso básico al sistema'),
    ('support', 'Soporte técnico con acceso a tickets')
ON CONFLICT (name) DO NOTHING;

-- Insertar permisos básicos
INSERT INTO permissions (name, description, resource, action) VALUES
    -- Permisos de usuarios
    ('users.read', 'Ver usuarios', 'users', 'read'),
    ('users.create', 'Crear usuarios', 'users', 'create'),
    ('users.update', 'Actualizar usuarios', 'users', 'update'),
    ('users.delete', 'Eliminar usuarios', 'users', 'delete'),
    
    -- Permisos de vendedores
    ('vendors.read', 'Ver vendedores', 'vendors', 'read'),
    ('vendors.create', 'Crear vendedores', 'vendors', 'create'),
    ('vendors.update', 'Actualizar vendedores', 'vendors', 'update'),
    ('vendors.delete', 'Eliminar vendedores', 'vendors', 'delete'),
    
    -- Permisos de tiendas
    ('stores.read', 'Ver tiendas', 'stores', 'read'),
    ('stores.create', 'Crear tiendas', 'stores', 'create'),
    ('stores.update', 'Actualizar tiendas', 'stores', 'update'),
    ('stores.delete', 'Eliminar tiendas', 'stores', 'delete'),
    
    -- Permisos de tickets
    ('tickets.read', 'Ver tickets', 'tickets', 'read'),
    ('tickets.create', 'Crear tickets', 'tickets', 'create'),
    ('tickets.update', 'Actualizar tickets', 'tickets', 'update'),
    ('tickets.delete', 'Eliminar tickets', 'tickets', 'delete'),
    ('tickets.assign', 'Asignar tickets', 'tickets', 'assign'),
    
    -- Permisos de gamificación
    ('gamification.read', 'Ver datos de gamificación', 'gamification', 'read'),
    ('gamification.update', 'Actualizar datos de gamificación', 'gamification', 'update'),
    
    -- Permisos de recompensas
    ('rewards.read', 'Ver recompensas', 'rewards', 'read'),
    ('rewards.create', 'Crear recompensas', 'rewards', 'create'),
    ('rewards.update', 'Actualizar recompensas', 'rewards', 'update'),
    ('rewards.delete', 'Eliminar recompensas', 'rewards', 'delete'),
    
    -- Permisos de CRM
    ('crm.read', 'Ver datos de CRM', 'crm', 'read'),
    ('crm.create', 'Crear campañas CRM', 'crm', 'create'),
    ('crm.update', 'Actualizar datos de CRM', 'crm', 'update'),
    
    -- Permisos de notificaciones
    ('notifications.read', 'Ver notificaciones', 'notifications', 'read'),
    ('notifications.send', 'Enviar notificaciones', 'notifications', 'send'),
    
    -- Permisos de sistema
    ('system.admin', 'Acceso administrativo completo', 'system', 'admin'),
    ('system.logs', 'Ver logs del sistema', 'system', 'logs')
ON CONFLICT (name) DO NOTHING;

-- Asignar permisos al rol admin (todos los permisos)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'admin'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Asignar permisos al rol vendor
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'vendor' 
AND p.name IN (
    'stores.read', 'stores.create', 'stores.update', 'stores.delete',
    'tickets.read', 'tickets.update', 'tickets.assign',
    'gamification.read', 'gamification.update',
    'rewards.read', 'rewards.create', 'rewards.update',
    'crm.read', 'crm.create', 'crm.update',
    'notifications.read', 'notifications.send'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Asignar permisos al rol user
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'user' 
AND p.name IN (
    'tickets.read', 'tickets.create', 'tickets.update',
    'gamification.read',
    'rewards.read',
    'notifications.read'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Asignar permisos al rol support
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'support' 
AND p.name IN (
    'tickets.read', 'tickets.update', 'tickets.assign',
    'users.read',
    'notifications.read', 'notifications.send'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Crear usuario administrador por defecto (password: admin123)
-- Nota: En producción, cambiar la contraseña inmediatamente
INSERT INTO users (username, email, email_hash, password_hash, first_name, last_name, is_admin, is_active, role) VALUES
    ('admin', 'admin@tfg.com', 'admin@tfg.com', crypt('admin123', gen_salt('bf')), 'Administrador', 'Sistema', TRUE, TRUE, 'admin')
ON CONFLICT (username) DO NOTHING;

-- Asignar rol admin al usuario administrador
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT (user_id, role_id) DO NOTHING;
