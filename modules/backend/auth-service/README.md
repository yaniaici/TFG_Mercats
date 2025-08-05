# Servicio de Autenticación

Servicio dedicado para manejar la autenticación y autorización del sistema de análisis de tickets.

## 🚀 Características

- **Registro de usuarios** con hash de contraseñas
- **Login/Logout** con JWT tokens
- **Verificación de tokens** 
- **Refresh de tokens**
- **Gestión de usuarios** (CRUD básico)
- **Integración con PostgreSQL**

## 📁 Estructura

```
auth-service/
├── main.py              # 🚀 Aplicación FastAPI
├── config.py            # ⚙️ Configuración
├── database.py          # 🗄️ Conexión BD
├── models.py            # 📊 Modelo User
├── schemas.py           # 📝 Esquemas Pydantic
├── auth.py              # 🔐 Funciones JWT
├── requirements.txt     # 📦 Dependencias
├── Dockerfile           # 🐳 Docker
├── env.example          # 🔧 Variables entorno
└── README.md            # 📖 Este archivo
```

## 🔧 Endpoints

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión
- `POST /auth/verify` - Verificar token
- `POST /auth/refresh` - Refrescar token

### Usuarios
- `GET /users/me` - Obtener usuario actual
- `PUT /users/me` - Actualizar usuario actual
- `GET /users/{user_id}` - Obtener usuario específico

### Sistema
- `GET /` - Información del servicio
- `GET /health` - Estado del servicio

## 🚀 Ejecución

### Con Docker
```bash
docker-compose up auth-service
```

### Localmente
```bash
cd modules/backend/auth-service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## 🔧 Configuración

### Variables de entorno
- `DATABASE_URL` - URL de conexión a PostgreSQL
- `SECRET_KEY` - Clave secreta para JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Tiempo de expiración de tokens
- `PORT` - Puerto del servicio (8001 por defecto)

### Ejemplo de uso

```python
import requests

# Registrar usuario
response = requests.post("http://localhost:8001/auth/register", json={
    "email_hash": "hash_del_email",
    "password": "contraseña123",
    "preferences": {}
})

# Login
response = requests.post("http://localhost:8001/auth/login", json={
    "email_hash": "hash_del_email",
    "password": "contraseña123"
})

token = response.json()["access_token"]

# Usar token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8001/users/me", headers=headers)
```

## 🔐 Seguridad

- **Contraseñas hasheadas** con bcrypt
- **JWT tokens** para autenticación
- **Verificación de tokens** en cada request
- **Tokens con expiración** configurable
- **Refresh de tokens** automático

## 🔗 Integración

Este servicio se integra con:
- **PostgreSQL** - Base de datos de usuarios
- **main-backend** - Servicio principal (consulta tokens)
- **API Gateway** - Enrutamiento de requests

## 📊 Monitoreo

- **Health check** en `/health`
- **Logs** configurables
- **Métricas** de autenticación

## 🧪 Testing

```bash
# Probar endpoints
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email_hash": "test@example.com", "password": "test123"}'

curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email_hash": "test@example.com", "password": "test123"}'
``` 