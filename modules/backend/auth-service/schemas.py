from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email_hash: str = Field(..., description="Hash del email del usuario")
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="Preferencias del usuario")

class UserCreate(UserBase):
    password: str = Field(..., description="Contraseña del usuario")

class UserUpdate(BaseModel):
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="Preferencias del usuario")

class UserLogin(BaseModel):
    email_hash: str = Field(..., description="Hash del email del usuario")
    password: str = Field(..., description="Contraseña del usuario")

class UserResponse(UserBase):
    id: UUID
    registration_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 