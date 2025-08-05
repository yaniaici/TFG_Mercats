from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import requests
import os

from database import get_db
from models import User
from config import settings

# Configuración del servicio de autenticación
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Obtener el usuario actual consultando al auth-service"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # Verificar token con el auth-service
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/verify",
            json={"token": token},
            timeout=5
        )
        
        if response.status_code != 200:
            raise credentials_exception
            
        user_data = response.json()
        user_id = user_data.get("user_id")
        
        if not user_id:
            raise credentials_exception
            
    except (requests.RequestException, KeyError):
        raise credentials_exception
    
    # Obtener usuario de la base de datos local
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    return user 