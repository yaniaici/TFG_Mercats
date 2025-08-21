from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

# Esquemas para MarketStore
class MarketStoreBase(BaseModel):
    name: str = Field(..., description="Nombre de la tienda del mercado")
    description: Optional[str] = Field(None, description="Descripción de la tienda")

class MarketStoreCreate(MarketStoreBase):
    pass

class MarketStoreUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nombre de la tienda del mercado")
    description: Optional[str] = Field(None, description="Descripción de la tienda")
    is_active: Optional[bool] = Field(None, description="Si la tienda está activa")

class MarketStoreResponse(MarketStoreBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas para Ticket
class TicketBase(BaseModel):
    original_filename: str = Field(..., description="Nombre original del archivo")
    ticket_metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadatos del ticket")

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Estado del ticket (pending, done_rejected, done_approved, failed)")
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
    
    @property
    def display_name(self) -> str:
        """Nombre para mostrar del ticket"""
        if self.ticket_metadata.get("type") == "digital":
            store_name = self.ticket_metadata.get("store_name", "Ticket Digital")
            return f"Ticket Digital - {store_name}"
        
        # Para tickets escaneados, usar el nombre de la tienda si está disponible
        store_name = self.processing_result.get("tienda", "Tienda del Mercat")
        return f"Compra - {store_name}"
    
    @property
    def store_name(self) -> str:
        """Nombre de la tienda"""
        if self.ticket_metadata.get("type") == "digital":
            return self.ticket_metadata.get("store_name", "Tienda Digital")
        return self.processing_result.get("tienda", "Desconocida")
    
    @property
    def total_amount(self) -> float:
        """Total del ticket"""
        if self.ticket_metadata.get("type") == "digital":
            return self.ticket_metadata.get("total_amount", 0.0)
        return self.processing_result.get("total", 0.0)
    
    @property
    def products(self) -> List[Dict[str, Any]]:
        """Productos del ticket"""
        if self.ticket_metadata.get("type") == "digital":
            return self.ticket_metadata.get("products", [])
        return self.processing_result.get("productos", [])
    
    @property
    def is_digital(self) -> bool:
        """Si es un ticket digital"""
        return self.ticket_metadata.get("type") == "digital"
    
    class Config:
        from_attributes = True
        
    def to_response_dict(self) -> dict:
        """Convertir a diccionario incluyendo propiedades computadas"""
        d = self.dict()
        d['display_name'] = self.display_name
        d['store_name'] = self.store_name
        d['total_amount'] = self.total_amount
        d['products'] = self.products
        d['is_digital'] = self.is_digital
        return d

class TicketUploadResponse(BaseModel):
    message: str
    ticket: TicketResponse

# Esquemas para el procesamiento de IA
class TicketProcessingResult(BaseModel):
    fecha: Optional[str] = Field(None, description="Fecha del ticket")
    hora: Optional[str] = Field(None, description="Hora del ticket")
    tienda: Optional[str] = Field(None, description="Nombre de la tienda")
    total: Optional[float] = Field(None, description="Total del ticket")
    tipo_ticket: Optional[str] = Field(None, description="Tipo de ticket")
    productos: List[Dict[str, Any]] = Field(default=[], description="Lista de productos")
    num_productos: int = Field(default=0, description="Número de productos")
    procesado_correctamente: bool = Field(default=False, description="Si el procesamiento fue exitoso")
    es_tienda_mercado: bool = Field(default=False, description="Si la tienda es del mercado")
    duplicate_detected: bool = Field(default=False, description="Si se detectó un ticket duplicado")
    status_message: Optional[str] = Field(None, description="Mensaje de estado del procesamiento")
    error: Optional[str] = Field(None, description="Error si el procesamiento falló") 