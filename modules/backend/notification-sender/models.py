from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=True)
    preferences = Column(JSONB, default={})
    registration_date = Column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="queued")  # queued, sent, failed
    meta = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_notifications_user_id', 'user_id'),
        Index('idx_notifications_campaign_id', 'campaign_id'),
        Index('idx_notifications_status', 'status'),
    )


class UserSubscription(Base):
    """Tabla para almacenar suscripciones de usuarios a diferentes canales"""
    __tablename__ = "user_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    channel = Column(String(20), nullable=False)  # webpush, android, ios
    subscription_data = Column(JSONB, nullable=False)  # Datos específicos del canal
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_user_subscriptions_user_id', 'user_id'),
        Index('idx_user_subscriptions_channel', 'channel'),
        Index('idx_user_subscriptions_active', 'is_active'),
    )

