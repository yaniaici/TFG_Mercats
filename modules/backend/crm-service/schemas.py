from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class SegmentCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    # Prompt opcional para derivar preferencias con IA
    prompt: Optional[str] = None


class SegmentResponse(SegmentCreate):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    # Si no se envía, el backend intentará generarlo con IA a partir de los segmentos
    message: Optional[str] = None
    segment_ids: List[UUID] = Field(default_factory=list)


class CampaignResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    message: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    segment_ids: List[UUID] = Field(default_factory=list)

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    campaign_id: Optional[UUID]
    message: str
    status: str
    meta: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationMarkSent(BaseModel):
    delivery_info: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AIGeneratePayload(BaseModel):
    prompt: str
    system: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 256


