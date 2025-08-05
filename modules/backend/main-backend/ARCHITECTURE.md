# Arquitectura del Backend Principal

## 📁 Estructura de Archivos

```
main-backend/
├── main.py              # 🚀 Aplicación FastAPI principal
├── config.py            # ⚙️ Configuración centralizada
├── database.py          # 🗄️ Conexión y sesiones de BD
├── models.py            # 📊 Modelos SQLAlchemy (tablas)
├── schemas.py           # 📝 Esquemas Pydantic (validación)
├── auth.py              # 🔐 Autenticación JWT
├── requirements.txt     # 📦 Dependencias
├── Dockerfile           # 🐳 Configuración Docker
├── env.example          # 🔧 Variables de entorno
├── README.md            # 📖 Documentación
├── test_backend.py      # 🧪 Script de pruebas
└── ARCHITECTURE.md      # 📋 Este archivo
```

## 🔧 Responsabilidades de cada archivo

### **main.py** - Aplicación Principal
- ✅ **Hace**: Define todos los endpoints de la API
- ✅ **Responsabilidad**: Lógica de negocio y rutas HTTP
- ✅ **No hace**: No crea tablas (eso lo hace PostgreSQL)

### **config.py** - Configuración Centralizada
- ✅ **Hace**: Centraliza todas las variables de entorno
- ✅ **Responsabilidad**: Configuración de BD, seguridad, servidor
- ✅ **Ventaja**: Un solo lugar para cambiar configuraciones

### **database.py** - Conexión a Base de Datos
- ✅ **Hace**: Configura conexión a PostgreSQL
- ✅ **Responsabilidad**: Engine, sesiones, función get_db()
- ✅ **No hace**: No define tablas (eso lo hace models.py)

### **models.py** - Modelos de Datos
- ✅ **Hace**: Define las tablas como clases Python + índices
- ✅ **Responsabilidad**: Estructura de datos, relaciones y optimización
- ✅ **No hace**: No crea tablas físicamente (eso lo hace SQLAlchemy)

### **schemas.py** - Validación de Datos
- ✅ **Hace**: Define cómo se validan los datos de entrada/salida
- ✅ **Responsabilidad**: Validación con Pydantic
- ✅ **Ventaja**: Validación automática de tipos y formatos

### **auth.py** - Autenticación
- ✅ **Hace**: Maneja JWT tokens y autenticación
- ✅ **Responsabilidad**: Login, verificación de tokens
- ✅ **Integración**: Usa config.py para configuración

## 🗄️ Flujo de Base de Datos

```
1. PostgreSQL (Docker) 
   ↓ (extensiones, triggers, vistas)
2. Base de datos inicializada
   ↓ (conexión)
3. database.py (engine + sesiones)
   ↓ (mapeo)
4. models.py (clases Python + índices)
   ↓ (creación automática)
5. Base.metadata.create_all() (tablas)
   ↓ (validación)
6. schemas.py (Pydantic)
   ↓ (lógica)
7. main.py (endpoints)
```

## 🔄 Flujo de una Petición

```
Cliente → main.py → schemas.py → models.py → database.py → PostgreSQL
   ↑                                                           ↓
   ← main.py ← schemas.py ← models.py ← database.py ← PostgreSQL
```

## ❌ Lo que NO hace cada archivo

### **main.py**
- ❌ No maneja configuración
- ❌ No valida datos directamente
- ✅ **Sí hace**: Crea tablas automáticamente con `Base.metadata.create_all()`

### **database.py**
- ❌ No define estructura de tablas
- ❌ No maneja autenticación
- ❌ No contiene lógica de negocio

### **models.py**
- ❌ No valida datos de entrada
- ❌ No maneja conexiones
- ✅ **Sí hace**: Define índices para optimización

### **schemas.py**
- ❌ No interactúa con BD directamente
- ❌ No contiene lógica de negocio
- ❌ No maneja autenticación

## ✅ Ventajas de esta arquitectura

1. **Separación de responsabilidades**: Cada archivo tiene una función específica
2. **Configuración centralizada**: Todo en config.py
3. **Sin duplicación**: Las tablas se crean una sola vez (PostgreSQL)
4. **Fácil mantenimiento**: Cambios aislados por archivo
5. **Escalabilidad**: Fácil agregar nuevas funcionalidades

## 🚀 Cómo agregar nuevas funcionalidades

### 1. Nuevo modelo de datos
```python
# En models.py
class NewModel(Base):
    __tablename__ = "new_table"
    # ... campos
```

### 2. Nuevo esquema
```python
# En schemas.py
class NewModelCreate(BaseModel):
    # ... campos
```

### 3. Nuevo endpoint
```python
# En main.py
@app.post("/new-endpoint")
async def new_endpoint(data: NewModelCreate, db: Session = Depends(get_db)):
    # ... lógica
```

### 4. Nueva configuración
```python
# En config.py
class Settings:
    NEW_SETTING: str = os.getenv("NEW_SETTING", "default")
```

## 🔍 Debugging

### Verificar conexión a BD
```python
# En main.py, agregar endpoint de debug
@app.get("/debug/db")
async def debug_db():
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        return {"status": "DB connected"}
    except Exception as e:
        return {"status": "DB error", "error": str(e)}
```

### Verificar configuración
```python
# En main.py, agregar endpoint de debug
@app.get("/debug/config")
async def debug_config():
    return {
        "database_url": settings.DATABASE_URL,
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL
    }
``` 