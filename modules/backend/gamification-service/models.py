from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class UserGamification(Base):
    """Modelo para el perfil de gamificación del usuario"""
    __tablename__ = "user_gamification"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)  # Referencia al usuario
    level = Column(Integer, default=1)  # Nivel actual del usuario
    experience = Column(Integer, default=0)  # Experiencia total acumulada
    total_tickets = Column(Integer, default=0)  # Total de tickets escaneados
    valid_tickets = Column(Integer, default=0)  # Total de tickets válidos
    total_spent = Column(Float, default=0.0)  # Total gastado en euros
    streak_days = Column(Integer, default=0)  # Días consecutivos escaneando
    last_scan_date = Column(DateTime(timezone=True), nullable=True)  # Última fecha de escaneo
    badges_earned = Column(Integer, default=0)  # Número de insignias ganadas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserBadge(Base):
    """Modelo para las insignias ganadas por el usuario"""
    __tablename__ = "user_badges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Referencia al usuario
    badge_type = Column(String(100), nullable=False)  # Tipo de insignia
    badge_name = Column(String(255), nullable=False)  # Nombre de la insignia
    badge_description = Column(String(500), nullable=False)  # Descripción de la insignia
    earned_at = Column(DateTime(timezone=True), server_default=func.now())  # Fecha de obtención
    is_active = Column(Boolean, default=True)  # Si la insignia está activa

class ExperienceLog(Base):
    """Modelo para el log de experiencia ganada"""
    __tablename__ = "experience_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Referencia al usuario
    ticket_id = Column(UUID(as_uuid=True), nullable=True)  # Referencia al ticket (opcional)
    experience_gained = Column(Integer, nullable=False)  # Experiencia ganada
    reason = Column(String(255), nullable=False)  # Razón por la que se ganó experiencia
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Reward(Base):
    """Modelo para las recompensas disponibles"""
    __tablename__ = "rewards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)  # Nombre de la recompensa
    description = Column(String(500), nullable=False)  # Descripción de la recompensa
    points_cost = Column(Integer, nullable=False)  # Costo en puntos
    reward_type = Column(String(100), nullable=False)  # Tipo de recompensa (parking, discount, etc.)
    reward_value = Column(String(255), nullable=False)  # Valor de la recompensa (ej: "1 hora", "10% descuento")
    is_active = Column(Boolean, default=True)  # Si la recompensa está disponible
    max_redemptions = Column(Integer, nullable=True)  # Máximo número de canjes (null = ilimitado)
    current_redemptions = Column(Integer, default=0)  # Número actual de canjes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class RewardRedemption(Base):
    """Modelo para el historial de canjes de recompensas"""
    __tablename__ = "reward_redemptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Referencia al usuario
    reward_id = Column(UUID(as_uuid=True), ForeignKey("rewards.id"), nullable=False)  # Referencia a la recompensa
    points_spent = Column(Integer, nullable=False)  # Puntos gastados
    redemption_code = Column(String(50), nullable=False, unique=True)  # Código único del canje
    is_used = Column(Boolean, default=False)  # Si la recompensa ha sido utilizada
    used_at = Column(DateTime(timezone=True), nullable=True)  # Fecha de uso
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Fecha de expiración
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SpecialReward(Base):
    """Modelo para recompensas especiales (0 puntos)"""
    __tablename__ = "special_rewards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)  # Nombre de la recompensa especial
    description = Column(String(500), nullable=False)  # Descripción de la recompensa
    reward_type = Column(String(100), nullable=False)  # Tipo de recompensa
    reward_value = Column(String(255), nullable=False)  # Valor de la recompensa
    is_global = Column(Boolean, default=False)  # Si es para todos los usuarios
    target_users = Column(JSONB, default=[])  # Lista de user_ids específicos
    target_segments = Column(JSONB, default=[])  # Lista de segmentos objetivo
    max_redemptions = Column(Integer, nullable=True)  # Máximo número de canjes por usuario
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Fecha de expiración
    is_active = Column(Boolean, default=True)  # Si la recompensa está activa
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_special_rewards_is_global', 'is_global'),
        Index('idx_special_rewards_is_active', 'is_active'),
        Index('idx_special_rewards_expires_at', 'expires_at'),
    )

class SpecialRewardRedemption(Base):
    """Modelo para el historial de canjes de recompensas especiales"""
    __tablename__ = "special_reward_redemptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Referencia al usuario
    special_reward_id = Column(UUID(as_uuid=True), ForeignKey("special_rewards.id"), nullable=False)  # Referencia a la recompensa especial
    redemption_code = Column(String(50), nullable=False, unique=True)  # Código único del canje
    is_used = Column(Boolean, default=False)  # Si la recompensa ha sido utilizada
    used_at = Column(DateTime(timezone=True), nullable=True)  # Fecha de uso
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_special_reward_redemptions_user_id', 'user_id'),
        Index('idx_special_reward_redemptions_special_reward_id', 'special_reward_id'),
    )

class UserNotification(Base):
    """Modelo para notificaciones personales del usuario"""
    __tablename__ = "user_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Referencia al usuario
    title = Column(String(255), nullable=False)  # Título de la notificación
    message = Column(Text, nullable=False)  # Mensaje de la notificación
    notification_type = Column(String(50), nullable=False)  # Tipo: 'reward', 'special_reward', 'system', 'promotion'
    is_read = Column(Boolean, default=False)  # Si la notificación ha sido leída
    related_id = Column(UUID(as_uuid=True), nullable=True)  # ID relacionado (reward_id, special_reward_id, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)  # Fecha de lectura

    __table_args__ = (
        Index('idx_user_notifications_user_id', 'user_id'),
        Index('idx_user_notifications_is_read', 'is_read'),
        Index('idx_user_notifications_created_at', 'created_at'),
    ) 