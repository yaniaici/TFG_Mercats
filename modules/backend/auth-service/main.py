from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import uvicorn
from datetime import datetime, timedelta
from passlib.context import CryptContext

from database import get_db, engine
from models import Base, User
from schemas import UserCreate, UserResponse, UserLogin, UserUpdate
from auth import create_access_token, get_current_user, verify_token
from config import settings

# Crear tablas si no existen (solo para auth-service)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Servicio de Autenticación",
    description="Servicio dedicado para autenticación y autorización",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

@app.get("/")
async def root():
    return {
        "message": "Servicio de Autenticación",
        "version": "1.0.0",
        "endpoints": {
            "register": "/auth/register",
            "login": "/auth/login",
            "verify": "/auth/verify",
            "refresh": "/auth/refresh",
            "users": "/users"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# ========================================
# ENDPOINTS DE AUTENTICACIÓN
# ========================================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.email_hash == user_data.email_hash).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )
    
    # Crear nuevo usuario
    hashed_password = pwd_context.hash(user_data.password)
    db_user = User(
        email_hash=user_data.email_hash,
        password_hash=hashed_password,
        preferences=user_data.preferences or {}
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/auth/login")
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión de usuario"""
    user = db.query(User).filter(User.email_hash == user_credentials.email_hash).first()
    
    if not user or not pwd_context.verify(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    # Crear token de acceso
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "user_id": str(user.id),
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/verify")
async def verify_token_endpoint(token: str = Body(..., embed=True)):
    """Verificar si un token es válido"""
    user_id = verify_token(token)
    if user_id:
        return {"valid": True, "user_id": user_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

@app.post("/auth/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refrescar token de acceso"""
    # Crear nuevo token
    access_token = create_access_token(data={"sub": str(current_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(current_user.id),
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# ========================================
# ENDPOINTS DE USUARIOS
# ========================================

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar información del usuario actual"""
    if user_data.preferences is not None:
        current_user.preferences = user_data.preferences
    
    current_user.updated_at = datetime.now()
    db.commit()
    db.refresh(current_user)
    
    return current_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Obtener información de un usuario específico"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 