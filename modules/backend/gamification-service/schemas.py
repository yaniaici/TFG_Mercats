from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class UserGamificationBase(BaseModel):
    """Esquema base para gamificación de usuario"""
    level: int = Field(..., description="Nivel actual del usuario")
    experience: int = Field(..., description="Experiencia total acumulada")
    total_tickets: int = Field(..., description="Total de tickets escaneados")
    valid_tickets: int = Field(..., description="Total de tickets válidos")
    total_spent: float = Field(..., description="Total gastado en euros")
    streak_days: int = Field(..., description="Días consecutivos escaneando")
    badges_earned: int = Field(..., description="Número de insignias ganadas")

class UserGamificationCreate(UserGamificationBase):
    """Esquema para crear perfil de gamificación"""
    user_id: uuid.UUID = Field(..., description="ID del usuario")

class UserGamificationResponse(UserGamificationBase):
    """Esquema de respuesta para gamificación de usuario"""
    id: uuid.UUID
    user_id: uuid.UUID
    last_scan_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserBadgeBase(BaseModel):
    """Esquema base para insignias de usuario"""
    badge_type: str = Field(..., description="Tipo de insignia")
    badge_name: str = Field(..., description="Nombre de la insignia")
    badge_description: str = Field(..., description="Descripción de la insignia")

class UserBadgeCreate(UserBadgeBase):
    """Esquema para crear insignia de usuario"""
    user_id: uuid.UUID = Field(..., description="ID del usuario")

class UserBadgeResponse(UserBadgeBase):
    """Esquema de respuesta para insignias de usuario"""
    id: uuid.UUID
    user_id: uuid.UUID
    earned_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class ExperienceLogBase(BaseModel):
    """Esquema base para log de experiencia"""
    experience_gained: int = Field(..., description="Experiencia ganada")
    reason: str = Field(..., description="Razón por la que se ganó experiencia")

class ExperienceLogCreate(ExperienceLogBase):
    """Esquema para crear log de experiencia"""
    user_id: uuid.UUID = Field(..., description="ID del usuario")
    ticket_id: Optional[uuid.UUID] = Field(None, description="ID del ticket (opcional)")

class ExperienceLogResponse(ExperienceLogBase):
    """Esquema de respuesta para log de experiencia"""
    id: uuid.UUID
    user_id: uuid.UUID
    ticket_id: Optional[uuid.UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class GamificationStats(BaseModel):
    """Esquema para estadísticas de gamificación"""
    level: int
    experience: int
    next_level_experience: int
    experience_to_next_level: int
    progress_percentage: float
    total_tickets: int
    valid_tickets: int
    total_spent: float
    streak_days: int
    badges_earned: int
    recent_badges: List[UserBadgeResponse] = []

class TicketProcessedEvent(BaseModel):
    """Esquema para evento de ticket procesado"""
    user_id: uuid.UUID
    ticket_id: uuid.UUID
    is_valid: bool
    total_amount: Optional[float] = None
    store_name: Optional[str] = None
    processing_date: datetime

# Nuevos schemas para recompensas
class RewardBase(BaseModel):
    """Esquema base para recompensas"""
    name: str = Field(..., description="Nombre de la recompensa")
    description: str = Field(..., description="Descripción de la recompensa")
    points_cost: int = Field(..., description="Costo en puntos")
    reward_type: str = Field(..., description="Tipo de recompensa")
    reward_value: str = Field(..., description="Valor de la recompensa")
    is_active: bool = Field(True, description="Si la recompensa está disponible")
    max_redemptions: Optional[int] = Field(None, description="Máximo número de canjes")

class RewardCreate(RewardBase):
    """Esquema para crear recompensa"""
    pass

class RewardResponse(RewardBase):
    """Esquema de respuesta para recompensas"""
    id: uuid.UUID
    current_redemptions: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RewardRedemptionBase(BaseModel):
    """Esquema base para canjes de recompensas"""
    user_id: uuid.UUID = Field(..., description="ID del usuario")
    reward_id: uuid.UUID = Field(..., description="ID de la recompensa")
    points_spent: int = Field(..., description="Puntos gastados")
    redemption_code: str = Field(..., description="Código único del canje")

class RewardRedemptionCreate(RewardRedemptionBase):
    """Esquema para crear canje de recompensa"""
    pass

class RewardRedemptionResponse(RewardRedemptionBase):
    """Esquema de respuesta para canjes de recompensas"""
    id: uuid.UUID
    is_used: bool
    used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    reward: RewardResponse  # Incluir información de la recompensa
    
    class Config:
        from_attributes = True

class RewardRedemptionWithReward(BaseModel):
    """Esquema para canje con información completa de la recompensa"""
    id: uuid.UUID
    user_id: uuid.UUID
    reward_id: uuid.UUID
    points_spent: int
    redemption_code: str
    is_used: bool
    used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    reward_name: str
    reward_description: str
    reward_type: str
    reward_value: str
    
    class Config:
        from_attributes = True 