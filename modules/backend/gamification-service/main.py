from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
import structlog
import secrets
from datetime import datetime, timedelta, timezone

from database import get_db
from models import UserGamification, UserBadge, ExperienceLog, Reward, RewardRedemption
from sqlalchemy import func
from schemas import (
    UserGamificationResponse, 
    UserBadgeResponse, 
    ExperienceLogResponse,
    GamificationStats,
    TicketProcessedEvent,
    RewardResponse,
    RewardRedemptionCreate,
    RewardRedemptionWithReward
)
from gamification_engine import GamificationEngine

# Configurar logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Gamification Service",
    description="Servicio de gamificación para el sistema de tickets",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Endpoint de salud del servicio"""
    return {"status": "healthy", "service": "gamification"}

@app.get("/users/{user_id}/stats", response_model=GamificationStats)
async def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    """Obtiene las estadísticas de gamificación del usuario"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    
    engine = GamificationEngine(db)
    stats = engine.get_user_stats(user_uuid)
    
    logger.info("Estadísticas obtenidas", user_id=user_id)
    return stats

@app.get("/users/{user_id}/profile", response_model=UserGamificationResponse)
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Obtiene el perfil de gamificación del usuario"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    
    engine = GamificationEngine(db)
    profile = engine.get_or_create_user_profile(user_uuid)
    
    logger.info("Perfil obtenido", user_id=user_id)
    return profile

@app.get("/users/{user_id}/badges", response_model=List[UserBadgeResponse])
async def get_user_badges(user_id: str, db: Session = Depends(get_db)):
    """Obtiene las insignias del usuario"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    
    badges = db.query(UserBadge).filter(
        UserBadge.user_id == user_uuid,
        UserBadge.is_active == True
    ).order_by(UserBadge.earned_at.desc()).all()
    
    logger.info("Insignias obtenidas", user_id=user_id, count=len(badges))
    return badges

@app.get("/users/{user_id}/experience-log", response_model=List[ExperienceLogResponse])
async def get_user_experience_log(user_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Obtiene el historial de experiencia del usuario"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    
    logs = db.query(ExperienceLog).filter(
        ExperienceLog.user_id == user_uuid
    ).order_by(ExperienceLog.created_at.desc()).limit(limit).all()
    
    logger.info("Historial de experiencia obtenido", user_id=user_id, count=len(logs))
    return logs

@app.post("/events/ticket-processed")
async def process_ticket_event(event: TicketProcessedEvent, db: Session = Depends(get_db)):
    """Procesa un evento de ticket procesado"""
    try:
        engine = GamificationEngine(db)
        profile = engine.process_ticket_event(event)
        
        logger.info("Evento de ticket procesado", 
                   user_id=str(event.user_id),
                   ticket_id=str(event.ticket_id),
                   is_valid=event.is_valid)
        
        return {
            "message": "Evento procesado correctamente",
            "user_id": str(event.user_id),
            "ticket_id": str(event.ticket_id),
            "profile_updated": True
        }
    except Exception as e:
        logger.error("Error procesando evento de ticket", 
                    error=str(e),
                    user_id=str(event.user_id),
                    ticket_id=str(event.ticket_id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando evento: {str(e)}"
        )

@app.post("/users/{user_id}/reset")
async def reset_user_gamification(user_id: str, db: Session = Depends(get_db)):
    """Resetea el perfil de gamificación del usuario"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    
    try:
        # Obtener perfil existente
        profile = db.query(UserGamification).filter(UserGamification.user_id == user_uuid).first()
        
        if profile:
            # Resetear valores
            profile.level = 1
            profile.experience = 0
            profile.total_tickets = 0
            profile.valid_tickets = 0
            profile.total_spent = 0.0
            profile.streak_days = 0
            profile.badges_earned = 0
            profile.last_scan_date = None
            
            # Eliminar insignias existentes
            db.query(UserBadge).filter(UserBadge.user_id == user_uuid).delete()
            
            # Eliminar logs de experiencia
            db.query(ExperienceLog).filter(ExperienceLog.user_id == user_uuid).delete()
            
            db.commit()
            
            logger.info("Perfil de gamificación reseteado", user_id=user_id)
            
            return {
                "message": "Perfil de gamificación reseteado correctamente",
                "user_id": user_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de gamificación no encontrado"
            )
            
    except Exception as e:
        logger.error("Error reseteando gamificación", 
                    error=str(e),
                    user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reseteando gamificación: {str(e)}"
        )

@app.post("/users/{user_id}/add-experience")
async def add_experience(
    user_id: str, 
    experience_gained: int, 
    reason: str, 
    ticket_id: str = None,
    db: Session = Depends(get_db)
):
    """Añade experiencia manualmente al usuario"""
    try:
        user_uuid = uuid.UUID(user_id)
        ticket_uuid = uuid.UUID(ticket_id) if ticket_id else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario o ticket inválido"
        )
    
    try:
        engine = GamificationEngine(db)
        profile = engine.add_experience(user_uuid, experience_gained, reason, ticket_uuid)
        
        logger.info("Experiencia añadida manualmente", 
                   user_id=user_id,
                   experience_gained=experience_gained,
                   reason=reason)
        
        return {
            "message": "Experiencia añadida correctamente",
            "user_id": user_id,
            "experience_gained": experience_gained,
            "new_total_experience": profile.experience,
            "new_level": profile.level
        }
    except Exception as e:
        logger.error("Error añadiendo experiencia", 
                    error=str(e),
                    user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error añadiendo experiencia: {str(e)}"
        )

# Nuevas rutas para recompensas
@app.get("/rewards", response_model=List[RewardResponse])
async def get_rewards(db: Session = Depends(get_db)):
    """Obtiene todas las recompensas disponibles"""
    try:
        rewards = db.query(Reward).filter(Reward.is_active == True).all()
        logger.info("Recompensas obtenidas", count=len(rewards))
        return rewards
    except Exception as e:
        logger.error("Error obteniendo recompensas", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo recompensas: {str(e)}"
        )

@app.get("/rewards/{reward_id}", response_model=RewardResponse)
async def get_reward(reward_id: str, db: Session = Depends(get_db)):
    """Obtiene una recompensa específica"""
    try:
        reward_uuid = uuid.UUID(reward_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de recompensa inválido"
        )
    
    try:
        reward = db.query(Reward).filter(Reward.id == reward_uuid).first()
        if not reward:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recompensa no encontrada"
            )
        
        logger.info("Recompensa obtenida", reward_id=reward_id)
        return reward
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error obteniendo recompensa", error=str(e), reward_id=reward_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo recompensa: {str(e)}"
        )

@app.post("/users/{user_id}/redeem-reward/{reward_id}")
async def redeem_reward(user_id: str, reward_id: str, db: Session = Depends(get_db)):
    """Canjea una recompensa por puntos"""
    try:
        user_uuid = uuid.UUID(user_id)
        reward_uuid = uuid.UUID(reward_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario o recompensa inválido"
        )
    
    try:
        # Verificar que la recompensa existe y está activa
        reward = db.query(Reward).filter(Reward.id == reward_uuid).first()
        if not reward:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recompensa no encontrada"
            )
        
        if not reward.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recompensa no disponible"
            )
        
        # Verificar límite de canjes
        if reward.max_redemptions and reward.current_redemptions >= reward.max_redemptions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recompensa agotada"
            )
        
        # Obtener perfil del usuario
        profile = db.query(UserGamification).filter(UserGamification.user_id == user_uuid).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de usuario no encontrado"
            )
        
        # Verificar que tiene suficientes puntos
        if profile.experience < reward.points_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No tienes suficientes puntos. Necesitas {reward.points_cost} puntos"
            )
        
        # Generar código único de canje
        redemption_code = secrets.token_hex(8).upper()
        
        # Crear el canje
        redemption = RewardRedemption(
            user_id=user_uuid,
            reward_id=reward_uuid,
            points_spent=reward.points_cost,
            redemption_code=redemption_code,
            expires_at=datetime.utcnow() + timedelta(days=30)  # Expira en 30 días
        )
        
        # Descontar puntos del usuario
        profile.experience -= reward.points_cost
        
        # Incrementar contador de canjes de la recompensa
        reward.current_redemptions += 1
        
        # Guardar cambios
        db.add(redemption)
        db.commit()
        
        logger.info("Recompensa canjeada", 
                   user_id=user_id,
                   reward_id=reward_id,
                   points_spent=reward.points_cost,
                   redemption_code=redemption_code)
        
        return {
            "message": "Recompensa canjeada correctamente",
            "redemption_code": redemption_code,
            "reward_name": reward.name,
            "points_spent": reward.points_cost,
            "remaining_points": profile.experience,
            "expires_at": redemption.expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Error canjeando recompensa", 
                    error=str(e),
                    user_id=user_id,
                    reward_id=reward_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error canjeando recompensa: {str(e)}"
        )

@app.get("/users/{user_id}/redemptions", response_model=List[RewardRedemptionWithReward])
async def get_user_redemptions(
    user_id: str,
    status_filter: str | None = Query(None, description="Filtrar por estado: available|used|expired"),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de canjes del usuario"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    
    try:
        # Obtener canjes con información de recompensa
        query = db.query(
            RewardRedemption,
            Reward.name.label('reward_name'),
            Reward.description.label('reward_description'),
            Reward.reward_type.label('reward_type'),
            Reward.reward_value.label('reward_value')
        ).join(
            Reward, RewardRedemption.reward_id == Reward.id
        ).filter(
            RewardRedemption.user_id == user_uuid
        )

        # Aplicar filtros por estado si se solicita
        now = datetime.now(timezone.utc)
        if status_filter == "available":
            query = query.filter(
                RewardRedemption.is_used == False,
                ((RewardRedemption.expires_at == None) | (RewardRedemption.expires_at > now))
            )
        elif status_filter == "used":
            query = query.filter(RewardRedemption.is_used == True)
        elif status_filter == "expired":
            query = query.filter(
                RewardRedemption.is_used == False,
                (RewardRedemption.expires_at != None),
                (RewardRedemption.expires_at <= now)
            )

        redemptions = query.order_by(
            RewardRedemption.created_at.desc()
        ).all()
        
        # Convertir a formato de respuesta
        result = []
        for redemption, reward_name, reward_description, reward_type, reward_value in redemptions:
            result.append(RewardRedemptionWithReward(
                id=redemption.id,
                user_id=redemption.user_id,
                reward_id=redemption.reward_id,
                points_spent=redemption.points_spent,
                redemption_code=redemption.redemption_code,
                is_used=redemption.is_used,
                used_at=redemption.used_at,
                expires_at=redemption.expires_at,
                created_at=redemption.created_at,
                updated_at=redemption.updated_at,
                reward_name=reward_name,
                reward_description=reward_description,
                reward_type=reward_type,
                reward_value=reward_value
            ))
        
        logger.info("Historial de canjes obtenido", user_id=user_id, count=len(result))
        return result
        
    except Exception as e:
        logger.error("Error obteniendo historial de canjes", 
                    error=str(e),
                    user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo historial de canjes: {str(e)}"
        )

@app.post("/redemptions/{redemption_code}/expire")
async def expire_redemption(redemption_code: str, db: Session = Depends(get_db)):
    """Marca un canje como expirado (por acción del vendedor)."""
    try:
        normalized_code = (redemption_code or "").strip().upper()
        redemption = db.query(RewardRedemption).filter(
            func.lower(RewardRedemption.redemption_code) == normalized_code.lower()
        ).first()

        if not redemption:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código de canje no encontrado"
            )

        if redemption.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede expirar una recompensa ya utilizada"
            )

        # Si ya está expirada, informar
        if redemption.expires_at and redemption.expires_at <= datetime.now(timezone.utc):
            return {
                "message": "La recompensa ya estaba expirada",
                "redemption_code": normalized_code,
                "expires_at": redemption.expires_at.isoformat()
            }

        redemption.expires_at = datetime.now(timezone.utc)
        db.commit()

        logger.info("Recompensa marcada como expirada", redemption_code=normalized_code)

        return {
            "message": "Recompensa expirada correctamente",
            "redemption_code": normalized_code,
            "expires_at": redemption.expires_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Error expirando recompensa", error=str(e), redemption_code=redemption_code)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error expirando recompensa: {str(e)}"
        )

@app.post("/redemptions/{redemption_code}/use")
async def use_redemption(redemption_code: str, db: Session = Depends(get_db)):
    """Marca una recompensa como utilizada"""
    try:
        # Normalizar código (evitar falsos negativos por mayúsculas/espacios)
        normalized_code = (redemption_code or "").strip().upper()

        redemption = db.query(RewardRedemption).filter(
            func.lower(RewardRedemption.redemption_code) == normalized_code.lower()
        ).first()
        
        if not redemption:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código de canje no encontrado"
            )
        
        if redemption.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recompensa ya utilizada"
            )
        
        if redemption.expires_at and redemption.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recompensa expirada"
            )
        
        # Marcar como utilizada
        redemption.is_used = True
        redemption.used_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info("Recompensa marcada como utilizada", redemption_code=normalized_code)
        
        return {
            "message": "Recompensa utilizada correctamente",
            "redemption_code": normalized_code,
            "used_at": redemption.used_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Error utilizando recompensa", 
                    error=str(e),
                    redemption_code=normalized_code)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error utilizando recompensa: {str(e)}"
        )

@app.get("/redemptions/{redemption_code}")
async def validate_redemption(redemption_code: str, db: Session = Depends(get_db)):
    """Valida un código de canje sin marcarlo como usado.

    Devuelve información sobre si existe, si está usado, expirado y detalles de la recompensa.
    """
    try:
        # Normalizar código (evitar falsos negativos por mayúsculas/espacios)
        normalized_code = (redemption_code or "").strip().upper()

        redemption = db.query(RewardRedemption).filter(
            func.lower(RewardRedemption.redemption_code) == normalized_code.lower()
        ).first()

        if not redemption:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código de canje no encontrado"
            )

        reward = db.query(Reward).filter(Reward.id == redemption.reward_id).first()

        is_expired = bool(redemption.expires_at and redemption.expires_at < datetime.now(timezone.utc))
        is_valid = (not redemption.is_used) and (not is_expired)

        return {
            "valid": is_valid,
            "message": (
                "Recompensa válida y disponible" if is_valid else (
                    "Recompensa ya utilizada" if redemption.is_used else "Recompensa expirada"
                )
            ),
            "redemption_code": normalized_code,
            "reward_name": reward.name if reward else None,
            "reward_description": reward.description if reward else None,
            "reward_type": reward.reward_type if reward else None,
            "reward_value": reward.reward_value if reward else None,
            "used_at": redemption.used_at.isoformat() if redemption.used_at else None,
            "expires_at": redemption.expires_at.isoformat() if redemption.expires_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error validando recompensa", error=str(e), redemption_code=(redemption_code or "").strip())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validando recompensa: {str(e)}"
        )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005) 