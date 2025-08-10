from fastapi import FastAPI, HTTPException, Depends, status, Body, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import uvicorn
from datetime import datetime, timedelta
from passlib.context import CryptContext
import uuid

from database import get_db, engine
from models import Base, User, PurchaseHistory
from schemas import UserCreate, UserResponse, UserLogin, UserUpdate, PurchaseHistoryResponse, PurchaseHistorySummary, PurchaseHistoryCreate
from auth import create_access_token, get_current_user, verify_token
from purchase_history_service import PurchaseHistoryService
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

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    # Verificar si el usuario ya existe por email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )
    
    # Crear nuevo usuario
    hashed_password = pwd_context.hash(user_data.password)
    # Validar rol solicitado
    allowed_roles = {"user", "vendor", "admin"}
    role_value = user_data.role if (hasattr(user_data, 'role') and user_data.role in allowed_roles) else "user"
    
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        preferences=user_data.preferences or {},
        role=role_value
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Crear token de acceso automáticamente después del registro
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user,
        "user_id": str(db_user.id),
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/login")
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión de usuario"""
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
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
    
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    print(f"🔐 Token configurado para expirar en {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutos ({expires_in} segundos)")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "user_id": str(user.id),
        "expires_in": expires_in
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
    if user_data.role is not None:
        # Solo admins pueden cambiar roles (propios u otros vía endpoint admin)
        if current_user.role != 'admin':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo admin puede cambiar roles")
        current_user.role = user_data.role
    
    current_user.updated_at = datetime.now()
    db.commit()
    db.refresh(current_user)
    
    return current_user

# ========================================
# ENDPOINTS ADMIN
# ========================================

def require_admin(user: User):
    if user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere rol admin")


@app.get("/admin/users", response_model=List[UserResponse])
async def admin_list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)
    return db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()


@app.post("/admin/users/{user_id}/promote-vendor", response_model=UserResponse)
async def admin_promote_to_vendor(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    user.role = 'vendor'
    db.commit()
    db.refresh(user)
    return user


@app.post("/admin/users/{user_id}/promote-admin", response_model=UserResponse)
async def admin_promote_to_admin(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    user.role = 'admin'
    db.commit()
    db.refresh(user)
    return user


@app.get("/admin/vendors", response_model=List[UserResponse])
async def admin_list_vendors(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)
    return db.query(User).filter(User.role == 'vendor').order_by(User.created_at.desc()).offset(offset).limit(limit).all()


@app.get("/admin/overview")
async def admin_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_vendors = db.query(func.count(User.id)).filter(User.role == 'vendor').scalar() or 0
    total_admins = db.query(func.count(User.id)).filter(User.role == 'admin').scalar() or 0
    total_purchases = db.query(func.count(PurchaseHistory.id)).scalar() or 0
    total_spent = db.query(func.coalesce(func.sum(PurchaseHistory.total_amount), 0)).scalar() or 0
    return {
        "total_users": int(total_users),
        "total_vendors": int(total_vendors),
        "total_admins": int(total_admins),
        "total_purchases": int(total_purchases),
        "total_spent": float(total_spent),
    }


@app.get("/admin/users/{user_id}/purchase-history", response_model=List[PurchaseHistoryResponse])
async def admin_get_user_purchase_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)
    try:
        user_uuid = uuid.UUID(user_id)
        service = PurchaseHistoryService(db)
        purchases = service.get_user_purchase_history(user_uuid, limit=limit, offset=offset)
        return purchases
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de usuario inválido")


@app.get("/admin/users/{user_id}/purchase-summary", response_model=PurchaseHistorySummary)
async def admin_get_user_purchase_summary(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)
    try:
        user_uuid = uuid.UUID(user_id)
        service = PurchaseHistoryService(db)
        summary = service.get_user_purchase_summary(user_uuid)
        return summary
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de usuario inválido")

@app.get("/users/{user_id}/public-info")
async def get_user_public_info(user_id: str, db: Session = Depends(get_db)):
    """Obtener información pública de un usuario para el QR (sin autenticación)"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Extraer nombre del email o preferences
    username = "Usuari"
    if user.preferences and user.preferences.get('username'):
        username = user.preferences['username']
    elif user.email:
        # Usar la parte antes del @ del email como nombre
        username = user.email.split('@')[0]
    
    return {
        "id": str(user.id),
        "email": user.email,
        "name": username,
        "registration_date": user.registration_date
    }

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

# ========================================
# ENDPOINTS DE HISTORIAL DE COMPRAS
# ========================================

@app.post("/purchase-history/create", response_model=PurchaseHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_record(
    purchase_data: PurchaseHistoryCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo registro de compra (llamado desde ticket-service)"""
    try:
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == purchase_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar que no existe ya un registro para este ticket
        existing_purchase = db.query(PurchaseHistory)\
            .filter(PurchaseHistory.ticket_id == purchase_data.ticket_id)\
            .first()
        
        if existing_purchase:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un registro de compra para este ticket"
            )
        
        service = PurchaseHistoryService(db)
        purchase_record = service.create_purchase_record(purchase_data)
        
        return purchase_record
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando registro de compra: {str(e)}"
        )

@app.get("/purchase-history/ticket/{ticket_id}")
async def get_purchase_by_ticket_id(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """Obtener una compra específica por ID de ticket (para verificar existencia)"""
    try:
        ticket_uuid = uuid.UUID(ticket_id)
        service = PurchaseHistoryService(db)
        purchase = service.get_purchase_by_ticket_id(ticket_uuid)
        
        if purchase:
            return {"exists": True, "purchase_id": str(purchase.id)}
        else:
            return {"exists": False}
            
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de ticket inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando compra: {str(e)}"
        )

@app.get("/users/{user_id}/purchase-history", response_model=List[PurchaseHistoryResponse])
async def get_user_purchase_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener el historial de compras de un usuario"""
    # Verificar que el usuario actual puede acceder al historial
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este historial"
        )
    
    try:
        user_uuid = uuid.UUID(user_id)
        service = PurchaseHistoryService(db)
        purchases = service.get_user_purchase_history(user_uuid, limit=limit, offset=offset)
        return purchases
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo historial de compras: {str(e)}"
        )

@app.get("/users/{user_id}/purchase-summary", response_model=PurchaseHistorySummary)
async def get_user_purchase_summary(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un resumen del historial de compras de un usuario"""
    # Verificar que el usuario actual puede acceder al resumen
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este resumen"
        )
    
    try:
        user_uuid = uuid.UUID(user_id)
        service = PurchaseHistoryService(db)
        summary = service.get_user_purchase_summary(user_uuid)
        return summary
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo resumen de compras: {str(e)}"
        )

@app.get("/users/{user_id}/spending-by-period")
async def get_user_spending_by_period(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Número de días para el período"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener el gasto del usuario por período"""
    # Verificar que el usuario actual puede acceder a esta información
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    try:
        user_uuid = uuid.UUID(user_id)
        service = PurchaseHistoryService(db)
        spending_data = service.get_user_spending_by_period(user_uuid, days=days)
        return spending_data
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo gasto por período: {str(e)}"
        )

@app.get("/purchase-history/{purchase_id}", response_model=PurchaseHistoryResponse)
async def get_purchase_by_id(
    purchase_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una compra específica por ID"""
    try:
        purchase_uuid = uuid.UUID(purchase_id)
        purchase = db.query(PurchaseHistory).filter(PurchaseHistory.id == purchase_uuid).first()
        
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compra no encontrada"
            )
        
        # Verificar que el usuario actual puede acceder a esta compra
        if str(purchase.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a esta compra"
            )
        
        return purchase
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de compra inválido"
        )

@app.delete("/purchase-history/{purchase_id}")
async def delete_purchase_record(
    purchase_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un registro de compra"""
    try:
        purchase_uuid = uuid.UUID(purchase_id)
        purchase = db.query(PurchaseHistory).filter(PurchaseHistory.id == purchase_uuid).first()
        
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compra no encontrada"
            )
        
        # Verificar que el usuario actual puede eliminar esta compra
        if str(purchase.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar esta compra"
            )
        
        service = PurchaseHistoryService(db)
        success = service.delete_purchase_record(purchase_uuid)
        
        if success:
            return {"message": "Registro de compra eliminado correctamente"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error eliminando el registro de compra"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de compra inválido"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 