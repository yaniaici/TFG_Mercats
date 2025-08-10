from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)  # Email real del usuario (único)
    password_hash = Column(String(255), nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    preferences = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    role = Column(String(20), nullable=False, default="user")  # user | vendor | admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_users_role', 'role'),
    )

class PurchaseHistory(Base):
    __tablename__ = "purchase_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Referencia al usuario
    ticket_id = Column(UUID(as_uuid=True), nullable=False)  # Referencia al ticket procesado
    purchase_date = Column(DateTime(timezone=True), nullable=False)  # Fecha de la compra
    store_name = Column(String(255), nullable=False)  # Nombre de la tienda
    total_amount = Column(Float, nullable=False)  # Total de la compra
    products = Column(JSONB, default=[])  # Lista de productos comprados
    num_products = Column(Integer, default=0)  # Número total de productos
    ticket_type = Column(String(100), nullable=True)  # Tipo de ticket
    is_market_store = Column(Boolean, default=False)  # Si es tienda del mercado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 