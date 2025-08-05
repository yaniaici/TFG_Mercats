# Guía de Migración - Gestión de Base de Datos

## 🔄 Cambios Realizados

### ❌ **Antes (Sistema Anterior)**
- Scripts SQL manuales en `modules/databases/postgres/init-scripts/`
- Duplicación entre SQL y SQLAlchemy
- Conflictos potenciales entre scripts SQL y modelos Python
- Gestión manual de índices

### ✅ **Ahora (Sistema Actual)**
- **SQLAlchemy maneja todo**: Tablas, índices, relaciones
- **Creación automática**: `Base.metadata.create_all()` en main.py
- **Índices integrados**: Definidos directamente en los modelos
- **Sin duplicación**: Un solo lugar para definir la estructura

## 📁 Archivos Eliminados

```
modules/databases/postgres/init-scripts/
├── 02_create_tables.sql     ❌ ELIMINADO (reemplazado por SQLAlchemy)
└── 03_create_indexes.sql    ❌ ELIMINADO (integrado en models.py)
```

## 📁 Archivos Mantenidos

```
modules/databases/postgres/init-scripts/
├── 01_create_extensions.sql ✅ MANTENIDO (extensiones PostgreSQL)
├── 04_create_triggers.sql   ✅ MANTENIDO (auditoría automática)
└── 05_create_views.sql      ✅ MANTENIDO (vistas útiles)
```

## 🔧 Cómo Funciona Ahora

### 1. **Inicialización de PostgreSQL**
```bash
# Docker ejecuta automáticamente:
# - 01_create_extensions.sql (uuid-ossp, pgcrypto, etc.)
# - 04_create_triggers.sql (auditoría automática)
# - 05_create_views.sql (vistas para consultas)
```

### 2. **Creación de Tablas**
```python
# En main.py
Base.metadata.create_all(bind=engine)
# Esto crea automáticamente:
# - Todas las tablas definidas en models.py
# - Todos los índices definidos en __table_args__
# - Todas las relaciones y foreign keys
```

### 3. **Definición de Índices**
```python
# En models.py
class User(Base):
    __tablename__ = "users"
    # ... campos ...
    
    __table_args__ = (
        Index('idx_users_email_hash', 'email_hash'),
        Index('idx_users_registration_date', 'registration_date'),
        # ... más índices ...
    )
```

## 🚀 Ventajas del Nuevo Sistema

### ✅ **Simplicidad**
- Un solo lugar para definir estructura de datos
- Sin duplicación entre SQL y Python
- Menos archivos para mantener

### ✅ **Consistencia**
- SQLAlchemy garantiza que los modelos coincidan con las tablas
- Índices siempre sincronizados con la estructura
- Menos errores de configuración

### ✅ **Flexibilidad**
- Fácil agregar nuevos campos o índices
- Migraciones automáticas al reiniciar
- Desarrollo más rápido

### ✅ **Mantenimiento**
- Cambios en un solo lugar (models.py)
- Menos archivos para revisar
- Documentación integrada en el código

## 🔄 Migración de Datos

### Si ya tienes datos existentes:
1. **Hacer backup** de la base de datos actual
2. **Eliminar contenedores** existentes
3. **Recrear** con el nuevo sistema
4. **Restaurar datos** si es necesario

### Si es una instalación nueva:
- No se requiere migración, el sistema funciona automáticamente

## 🧪 Testing

### Verificar que todo funciona:
```bash
# 1. Ejecutar el sistema
docker-compose up

# 2. Verificar tablas creadas
docker exec -it tfg_postgres psql -U ticket_user -d ticket_analytics -c "\dt"

# 3. Verificar índices creados
docker exec -it tfg_postgres psql -U ticket_user -d ticket_analytics -c "\di"

# 4. Probar endpoints
python modules/backend/test_auth_integration.py
```

## 📊 Estructura Final

```
PostgreSQL Container
├── Extensiones (uuid-ossp, pgcrypto)
├── Triggers (auditoría automática)
├── Vistas (consultas complejas)
└── Tablas (creadas por SQLAlchemy)
    ├── users (con índices)
    ├── user_profiles (con índices)
    ├── tickets (con índices)
    ├── ticket_images (con índices)
    └── audit_logs (con índices)
```

## 🔍 Troubleshooting

### Problema: "Table already exists"
```bash
# Solución: Eliminar contenedor y recrear
docker-compose down -v
docker-compose up
```

### Problema: "Index already exists"
```bash
# Solución: Los índices se crean automáticamente
# Si hay conflictos, recrear contenedor
```

### Problema: "Extension not found"
```bash
# Verificar que 01_create_extensions.sql se ejecute
# Revisar logs del contenedor PostgreSQL
```

## 📝 Notas Importantes

1. **Siempre hacer backup** antes de cambios importantes
2. **Los triggers de auditoría** siguen funcionando automáticamente
3. **Las vistas** están disponibles para consultas complejas
4. **Los índices** se crean automáticamente con las tablas
5. **SQLAlchemy** maneja toda la estructura de datos

## 🎯 Próximos Pasos

- [ ] Implementar Alembic para migraciones más avanzadas
- [ ] Agregar más índices según patrones de uso
- [ ] Optimizar consultas usando las vistas existentes
- [ ] Implementar backup automático de datos 