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
INSERT INTO users (email, email_hash, password_hash, first_name, last_name, is_admin, is_active, role) VALUES
    ('admin@tfg.com', 'admin@tfg.com', crypt('admin123', gen_salt('bf')), 'Administrador', 'Sistema', TRUE, TRUE, 'admin')
ON CONFLICT (email) DO NOTHING;

-- Asignar rol admin al usuario administrador
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.email = 'admin@tfg.com' AND r.name = 'admin'
ON CONFLICT (user_id, role_id) DO NOTHING;

-- Insertar recompensas de ejemplo en catalán
INSERT INTO rewards (name, description, points_cost, reward_type, reward_value, is_active, max_redemptions) VALUES
    -- Recompensas de parking
    ('Estacionament Gratuït 1 Hora', 'Estacionament gratuït durant 1 hora al centre comercial', 100, 'parking', '1 hora', TRUE, 50),
    ('Estacionament Gratuït 2 Hores', 'Estacionament gratuït durant 2 hores al centre comercial', 200, 'parking', '2 hores', TRUE, 30),
    ('Estacionament Gratuït 4 Hores', 'Estacionament gratuït durant 4 hores al centre comercial', 350, 'parking', '4 hores', TRUE, 20),
    
    -- Recompensas de descuentos
    ('Descompte 5% en Moda', 'Descompte del 5% en totes les botigues de moda', 150, 'discount', '5% moda', TRUE, 100),
    ('Descompte 10% en Restaurants', 'Descompte del 10% en tots els restaurants del centre', 250, 'discount', '10% restaurants', TRUE, 75),
    ('Descompte 15% en Electrònica', 'Descompte del 15% en botigues d''electrònica', 400, 'discount', '15% electrònica', TRUE, 25),
    ('Descompte 20% en Llibres', 'Descompte del 20% en la llibreria del centre', 300, 'discount', '20% llibres', TRUE, 50),
    
    -- Recompensas de comida
    ('Cafè Gratuït', 'Un cafè gratuït en qualsevol cafeteria del centre', 50, 'food', '1 cafè', TRUE, 200),
    ('Entrepà Gratuït', 'Un entrepà gratuït en qualsevol restaurant del centre', 120, 'food', '1 entrepà', TRUE, 150),
    ('Gelat Gratuït', 'Un gelat gratuït en la gelateria del centre', 80, 'food', '1 gelat', TRUE, 100),
    ('Pizza Gratuïta', 'Una pizza gratuïta en el restaurant italià', 200, 'food', '1 pizza', TRUE, 80),
    
    -- Recompensas de merchandising
    ('Tassa del Centre', 'Una tassa commemorativa del centre comercial', 75, 'merchandise', '1 tassa', TRUE, 100),
    ('Bolsa Reutilitzable', 'Una bolsa reutilitzable del centre comercial', 60, 'merchandise', '1 bolsa', TRUE, 150),
    ('Llibreta Personalitzada', 'Una llibreta personalitzada del centre', 90, 'merchandise', '1 llibreta', TRUE, 80),
    ('Pulsera del Centre', 'Una pulsera commemorativa del centre comercial', 45, 'merchandise', '1 pulsera', TRUE, 200),
    
    -- Recompensas de experiencias
    ('Sessió de Cinema', 'Una entrada gratuïta per al cinema del centre', 300, 'experience', '1 entrada cinema', TRUE, 60),
    ('Classe de Cuina', 'Una classe de cuina gratuïta en el centre', 500, 'experience', '1 classe cuina', TRUE, 20),
    ('Massatge 15 Minuts', 'Un massatge de 15 minuts gratuït', 400, 'experience', '15 min massatge', TRUE, 30),
    ('Visita Guiada', 'Una visita guiada gratuïta del centre comercial', 150, 'experience', '1 visita guiada', TRUE, 40),
    
    -- Recompensas especiales
    ('Descompte 25% Black Friday', 'Descompte especial del 25% durant el Black Friday', 600, 'discount', '25% Black Friday', TRUE, 10),
    ('Pack Familiar', 'Pack familiar amb múltiples recompenses', 800, 'experience', 'Pack familiar', TRUE, 15),
    ('VIP Shopping Day', 'Dia VIP amb descomptes exclusius', 1000, 'experience', 'Dia VIP', TRUE, 5)
ON CONFLICT (name) DO NOTHING;
