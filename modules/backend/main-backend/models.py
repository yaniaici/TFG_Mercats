from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_hash = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    preferences = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    tickets = relationship("Ticket", back_populates="user")
    
    # Índices
    __table_args__ = (
        Index('idx_users_email_hash', 'email_hash'),
        Index('idx_users_registration_date', 'registration_date'),
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
    )

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_type = Column(String(50), default="regular")  # regular, turista, ciudadano
    segment = Column(String(100))  # Clúster o segmento de comportamiento
    gamification_points = Column(Integer, default=0)
    level = Column(Integer, default=1)  # Nivel de fidelización
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relación con el usuario
    user = relationship("User", back_populates="profile")
    
    # Índices
    __table_args__ = (
        Index('idx_user_profiles_user_id', 'user_id'),
        Index('idx_user_profiles_user_type', 'user_type'),
        Index('idx_user_profiles_segment', 'segment'),
        Index('idx_user_profiles_gamification_points', 'gamification_points'),
        Index('idx_user_profiles_level', 'level'),
    )

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    purchase_datetime = Column(DateTime(timezone=True), nullable=False)
    store_id = Column(String(100), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    origin = Column(String(50), nullable=False)  # escaneo, digital, API
    ticket_hash = Column(String(255))  # Hash del ticket para evitar duplicados
    processed = Column(Boolean, default=False)  # Indica si el ticket ha sido procesado por IA
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="tickets")
    images = relationship("TicketImage", back_populates="ticket")
    
    # Índices
    __table_args__ = (
        Index('idx_tickets_user_id', 'user_id'),
        Index('idx_tickets_purchase_datetime', 'purchase_datetime'),
        Index('idx_tickets_store_id', 'store_id'),
        Index('idx_tickets_origin', 'origin'),
        Index('idx_tickets_processed', 'processed'),
        Index('idx_tickets_ticket_hash', 'ticket_hash'),
        Index('idx_tickets_created_at', 'created_at'),
        Index('idx_tickets_user_date', 'user_id', 'purchase_datetime'),
    )

class TicketImage(Base):
    __tablename__ = "ticket_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(500), nullable=False)  # Ruta al archivo de imagen
    image_hash = Column(String(255), nullable=False)  # Hash de la imagen
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con el ticket
    ticket = relationship("Ticket", back_populates="images")
    
    # Índices
    __table_args__ = (
        Index('idx_ticket_images_ticket_id', 'ticket_id'),
        Index('idx_ticket_images_processed', 'processed'),
        Index('idx_ticket_images_expires_at', 'expires_at'),
        Index('idx_ticket_images_image_hash', 'image_hash'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Índices
    __table_args__ = (
        Index('idx_audit_logs_table_name', 'table_name'),
        Index('idx_audit_logs_record_id', 'record_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_created_at', 'created_at'),
        Index('idx_audit_logs_table_record', 'table_name', 'record_id', 'created_at'),
    ) 