from pydantic import BaseModel, Field
from typing import Optional, List, Union
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

# Esquemas para recompensas especiales
class SpecialRewardBase(BaseModel):
    """Esquema base para recompensas especiales"""
    name: str = Field(..., description="Nombre de la recompensa especial")
    description: str = Field(..., description="Descripción de la recompensa")
    reward_type: str = Field(..., description="Tipo de recompensa")
    reward_value: str = Field(..., description="Valor de la recompensa")
    is_global: bool = Field(False, description="Si es para todos los usuarios")
    target_users: List[str] = Field(default=[], description="Lista de user_ids específicos")
    target_segments: List[str] = Field(default=[], description="Lista de segmentos objetivo")
    max_redemptions: Optional[int] = Field(None, description="Máximo número de canjes por usuario")
    expires_at: Optional[Union[datetime, str]] = Field(None, description="Fecha de expiración")
    is_active: bool = Field(True, description="Si la recompensa está activa")

class SpecialRewardCreate(SpecialRewardBase):
    """Esquema para crear recompensa especial"""
    pass

class SpecialRewardResponse(SpecialRewardBase):
    """Esquema de respuesta para recompensas especiales"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SpecialRewardRedemptionBase(BaseModel):
    """Esquema base para canjes de recompensas especiales"""
    user_id: uuid.UUID = Field(..., description="ID del usuario")
    special_reward_id: uuid.UUID = Field(..., description="ID de la recompensa especial")
    redemption_code: str = Field(..., description="Código único del canje")

class SpecialRewardRedemptionCreate(SpecialRewardRedemptionBase):
    """Esquema para crear canje de recompensa especial"""
    pass

class SpecialRewardRedemptionResponse(SpecialRewardRedemptionBase):
    """Esquema de respuesta para canjes de recompensas especiales"""
    id: uuid.UUID
    is_used: bool
    used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    special_reward: SpecialRewardResponse  # Incluir información de la recompensa especial
    
    class Config:
        from_attributes = True

class SpecialRewardRedemptionSimpleResponse(BaseModel):
    """Esquema simplificado para canjes de recompensas especiales (sin special_reward)"""
    id: uuid.UUID
    user_id: uuid.UUID
    special_reward_id: uuid.UUID
    redemption_code: str
    is_used: bool
    used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SpecialRewardWithStatusResponse(BaseModel):
    """Esquema de respuesta para recompensas especiales con información de estado"""
    reward: SpecialRewardResponse
    is_redeemed: bool
    is_available: bool
    is_expired: bool
    redemption_count: int
    can_redeem: bool
    last_redemption: Optional[SpecialRewardRedemptionSimpleResponse] = None

# Esquemas para notificaciones personales
class UserNotificationBase(BaseModel):
    """Esquema base para notificaciones personales"""
    title: str = Field(..., description="Título de la notificación")
    message: str = Field(..., description="Mensaje de la notificación")
    notification_type: str = Field(..., description="Tipo: 'reward', 'special_reward', 'system', 'promotion'")
    related_id: Optional[uuid.UUID] = Field(None, description="ID relacionado")

class UserNotificationCreate(UserNotificationBase):
    """Esquema para crear notificación personal"""
    user_id: uuid.UUID = Field(..., description="ID del usuario")

class UserNotificationResponse(UserNotificationBase):
    """Esquema de respuesta para notificaciones personales"""
    id: uuid.UUID
    user_id: uuid.UUID
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationStats(BaseModel):
    """Esquema para estadísticas de notificaciones"""
    total_notifications: int
    unread_notifications: int
    notifications_by_type: dict

# Esquemas para el admin
class SpecialRewardDistributionRequest(BaseModel):
    """Esquema para solicitud de distribución de recompensas especiales"""
    special_reward_id: uuid.UUID
    target_type: str = Field(..., description="'global', 'users', 'segments'")
    target_ids: List[str] = Field(default=[], description="Lista de user_ids o segment_ids")
    send_notifications: bool = Field(True, description="Si enviar notificaciones")

class SpecialRewardDistributionResponse(BaseModel):
    """Esquema de respuesta para distribución de recompensas especiales"""
    success: bool
    message: str
    users_affected: int
    notifications_sent: int 