from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import requests
import os
from datetime import datetime

from database import get_db, engine
from models import Base, User, UserProfile, Ticket, TicketImage, AuditLog
from schemas import (
    UserProfileCreate, UserProfileResponse,
    TicketCreate, TicketResponse, TicketUpdate,
    GamificationResponse
)
from auth_client import get_current_user
from config import settings

# Crear tablas automáticamente con SQLAlchemy
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Análisis de Tickets - Backend",
    description="API completa para el sistema de análisis de tickets con gamificación",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración del servicio de autenticación
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

@app.get("/")
async def root():
    return {
        "message": "Sistema de Análisis de Tickets - Backend",
        "version": "1.0.0",
        "endpoints": {
            "tickets": "/tickets",
            "profiles": "/users/{user_id}/profile",
            "gamification": "/gamification",
            "analytics": "/analytics"
        },
        "note": "Autenticación manejada por auth-service en puerto 8001"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# ========================================
# ENDPOINTS DE DEBUG
# ========================================

@app.get("/debug/db")
async def debug_db():
    """Verificar conexión a la base de datos"""
    try:
        db = next(get_db())
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "DB connected", "message": "Conexión exitosa a PostgreSQL"}
    except Exception as e:
        return {"status": "DB error", "error": str(e)}

@app.get("/debug/config")
async def debug_config():
    """Verificar configuración de la aplicación"""
    return {
        "database_url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('://')[1], '***'),
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "host": settings.HOST,
        "port": settings.PORT
    }

# ========================================
# NOTA: AUTENTICACIÓN MANEJADA POR AUTH-SERVICE
# ========================================
# 
# Los endpoints de autenticación están en el auth-service (puerto 8001):
# - POST /auth/register - Registrar usuario
# - POST /auth/login - Iniciar sesión  
# - POST /auth/verify - Verificar token
# - POST /auth/refresh - Refrescar token
# - GET /users/me - Obtener usuario actual
# - PUT /users/me - Actualizar usuario actual
# - GET /users/{user_id} - Obtener usuario específico

# ========================================
# ENDPOINTS DE PERFILES DE USUARIO
# ========================================

@app.post("/users/{user_id}/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    user_id: str,
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """Crear perfil de usuario"""
    # Verificar si el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar si ya existe un perfil
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene un perfil"
        )
    
    # Crear perfil
    db_profile = UserProfile(
        user_id=user_id,
        user_type=profile_data.user_type,
        segment=profile_data.segment
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@app.get("/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Obtener perfil de usuario"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado"
        )
    return profile

@app.put("/users/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: str,
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """Actualizar perfil de usuario"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado"
        )
    
    profile.user_type = profile_data.user_type
    profile.segment = profile_data.segment
    profile.updated_at = datetime.now()
    
    db.commit()
    db.refresh(profile)
    
    return profile

# ========================================
# ENDPOINTS DE TICKETS
# ========================================

@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo ticket"""
    db_ticket = Ticket(
        user_id=str(current_user.id),
        purchase_datetime=ticket_data.purchase_datetime,
        store_id=ticket_data.store_id,
        total_price=ticket_data.total_price,
        origin=ticket_data.origin,
        ticket_hash=ticket_data.ticket_hash
    )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket

@app.get("/tickets", response_model=List[TicketResponse])
async def get_user_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Obtener tickets del usuario actual"""
    tickets = db.query(Ticket).filter(
        Ticket.user_id == str(current_user.id)
    ).offset(skip).limit(limit).all()
    
    return tickets

@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un ticket específico"""
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.user_id == str(current_user.id)
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    return ticket

@app.put("/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    ticket_data: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un ticket"""
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.user_id == str(current_user.id)
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    if ticket_data.processed is not None:
        ticket.processed = ticket_data.processed
    
    ticket.updated_at = datetime.now()
    db.commit()
    db.refresh(ticket)
    
    return ticket

# ========================================
# ENDPOINTS DE GAMIFICACIÓN
# ========================================

@app.get("/gamification/profile", response_model=GamificationResponse)
async def get_gamification_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener perfil de gamificación del usuario"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == str(current_user.id)).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de gamificación no encontrado"
        )
    
    return {
        "user_id": str(current_user.id),
        "points": profile.gamification_points,
        "level": profile.level,
        "user_type": profile.user_type,
        "segment": profile.segment
    }

@app.post("/gamification/add-points")
async def add_gamification_points(
    points: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Añadir puntos de gamificación al usuario"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == str(current_user.id)).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de gamificación no encontrado"
        )
    
    profile.gamification_points += points
    
    # Calcular nuevo nivel (cada 100 puntos = 1 nivel)
    new_level = (profile.gamification_points // 100) + 1
    if new_level > profile.level:
        profile.level = new_level
    
    profile.updated_at = datetime.now()
    db.commit()
    db.refresh(profile)
    
    return {
        "message": f"Puntos añadidos: {points}",
        "new_total": profile.gamification_points,
        "new_level": profile.level
    }

# ========================================
# ENDPOINTS DE ANALÍTICAS
# ========================================

@app.get("/analytics/user-stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas del usuario"""
    # Contar tickets totales
    total_tickets = db.query(Ticket).filter(
        Ticket.user_id == str(current_user.id)
    ).count()
    
    # Contar tickets procesados
    processed_tickets = db.query(Ticket).filter(
        Ticket.user_id == str(current_user.id),
        Ticket.processed == True
    ).count()
    
    # Calcular gasto total
    total_spent = db.query(Ticket).filter(
        Ticket.user_id == str(current_user.id)
    ).with_entities(db.func.sum(Ticket.total_price)).scalar() or 0
    
    # Obtener perfil
    profile = db.query(UserProfile).filter(UserProfile.user_id == str(current_user.id)).first()
    
    return {
        "total_tickets": total_tickets,
        "processed_tickets": processed_tickets,
        "total_spent": float(total_spent),
        "processing_rate": (processed_tickets / total_tickets * 100) if total_tickets > 0 else 0,
        "gamification_points": profile.gamification_points if profile else 0,
        "level": profile.level if profile else 1
    }

@app.get("/analytics/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db), limit: int = 10):
    """Obtener tabla de líderes por puntos de gamificación"""
    profiles = db.query(UserProfile).order_by(
        UserProfile.gamification_points.desc()
    ).limit(limit).all()
    
    return [
        {
            "user_id": str(profile.user_id),
            "points": profile.gamification_points,
            "level": profile.level,
            "user_type": profile.user_type
        }
        for profile in profiles
    ]

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 