from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# ========================================
# ESQUEMAS PARA USUARIOS
# ========================================

class UserBase(BaseModel):
    email_hash: str = Field(..., description="Hash del email del usuario")
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="Preferencias del usuario")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

class UserUpdate(BaseModel):
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="Preferencias del usuario")

class UserResponse(UserBase):
    id: UUID
    registration_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email_hash: str = Field(..., description="Hash del email del usuario")
    password: str = Field(..., description="Contraseña del usuario")

# ========================================
# ESQUEMAS PARA PERFILES DE USUARIO
# ========================================

class UserProfileBase(BaseModel):
    user_type: str = Field(default="regular", description="Tipo de usuario: regular, turista, ciudadano")
    segment: Optional[str] = Field(default=None, description="Segmento de comportamiento del usuario")

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    gamification_points: int
    level: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ========================================
# ESQUEMAS PARA TICKETS
# ========================================

class TicketBase(BaseModel):
    purchase_datetime: datetime = Field(..., description="Fecha y hora de la compra")
    store_id: str = Field(..., description="ID de la tienda")
    total_price: Decimal = Field(..., description="Precio total del ticket")
    origin: str = Field(..., description="Origen del ticket: escaneo, digital, API")
    ticket_hash: Optional[str] = Field(default=None, description="Hash del ticket")

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    processed: Optional[bool] = Field(default=None, description="Indica si el ticket ha sido procesado")

class TicketResponse(TicketBase):
    id: UUID
    user_id: Optional[UUID]
    processed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ========================================
# ESQUEMAS PARA IMÁGENES DE TICKETS
# ========================================

class TicketImageBase(BaseModel):
    image_path: str = Field(..., description="Ruta al archivo de imagen")
    image_hash: str = Field(..., description="Hash de la imagen")

class TicketImageCreate(TicketImageBase):
    pass

class TicketImageResponse(TicketImageBase):
    id: UUID
    ticket_id: UUID
    processed: bool
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True

# ========================================
# ESQUEMAS PARA GAMIFICACIÓN
# ========================================

class GamificationResponse(BaseModel):
    user_id: str
    points: int
    level: int
    user_type: str
    segment: Optional[str]

# ========================================
# ESQUEMAS PARA ANALÍTICAS
# ========================================

class UserStatsResponse(BaseModel):
    total_tickets: int
    processed_tickets: int
    total_spent: float
    processing_rate: float
    gamification_points: int
    level: int

class LeaderboardEntry(BaseModel):
    user_id: str
    points: int
    level: int
    user_type: str

# ========================================
# ESQUEMAS PARA AUTENTICACIÓN
# ========================================

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class TokenData(BaseModel):
    user_id: Optional[str] = None 