from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class TicketBase(BaseModel):
    original_filename: str = Field(..., description="Nombre original del archivo")
    ticket_metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadatos del ticket")

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Estado del ticket")
    ticket_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos del ticket")
    processing_result: Optional[Dict[str, Any]] = Field(None, description="Resultado del procesamiento")

class TicketResponse(TicketBase):
    id: UUID
    user_id: UUID
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    status: str
    processing_result: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TicketUploadResponse(BaseModel):
    message: str
    ticket: TicketResponse 