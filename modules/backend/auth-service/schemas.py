from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

# Esquemas para User
class UserBase(BaseModel):
    email: str = Field(..., description="Email del usuario")
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="Preferencias del usuario")
    role: str = Field(default="user", description="Rol del usuario: user | vendor | admin")

class UserCreate(UserBase):
    password: str = Field(..., description="Contraseña del usuario")
    role: Optional[str] = Field(default="user", description="Rol del usuario: user | vendor | admin")

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, description="Email del usuario")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Preferencias del usuario")
    is_active: Optional[bool] = Field(None, description="Si el usuario está activo")
    role: Optional[str] = Field(None, description="Rol del usuario")

class UserResponse(UserBase):
    id: UUID
    registration_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str
        }

# Esquemas para PurchaseHistory
class PurchaseHistoryBase(BaseModel):
    user_id: UUID = Field(..., description="ID del usuario")
    ticket_id: UUID = Field(..., description="ID del ticket procesado")
    purchase_date: datetime = Field(..., description="Fecha de la compra")
    store_name: str = Field(..., description="Nombre de la tienda")
    total_amount: float = Field(..., description="Total de la compra")
    products: List[Dict[str, Any]] = Field(default=[], description="Lista de productos comprados")
    num_products: int = Field(default=0, description="Número total de productos")
    ticket_type: Optional[str] = Field(None, description="Tipo de ticket")
    is_market_store: bool = Field(default=False, description="Si es tienda del mercado")

class PurchaseHistoryCreate(PurchaseHistoryBase):
    pass

class PurchaseHistoryResponse(PurchaseHistoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PurchaseHistorySummary(BaseModel):
    total_purchases: int = Field(..., description="Total de compras")
    total_spent: float = Field(..., description="Total gastado")
    favorite_store: Optional[str] = Field(None, description="Tienda favorita")
    most_purchased_products: List[Dict[str, Any]] = Field(default=[], description="Productos más comprados")
    last_purchase_date: Optional[datetime] = Field(None, description="Fecha de la última compra")
    average_purchase_amount: float = Field(..., description="Promedio por compra")

# Esquemas para autenticación
class UserLogin(BaseModel):
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")

class UserRegister(BaseModel):
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")
    confirm_password: str = Field(..., description="Confirmación de contraseña")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID

class TokenData(BaseModel):
    user_id: Optional[UUID] = None 