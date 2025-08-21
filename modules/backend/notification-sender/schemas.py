from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class ChannelType(str, Enum):
    """Tipos de canales de notificación disponibles"""
    WEBPUSH = "webpush"
    ANDROID = "android"
    IOS = "ios"


class NotificationSendRequest(BaseModel):
    """Solicitud para enviar una notificación"""
    user_id: UUID = Field(..., description="ID del usuario destinatario")
    message: str = Field(..., description="Mensaje de la notificación")
    title: str = Field(..., description="Título de la notificación")
    channel: ChannelType = Field(..., description="Canal de envío")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Datos adicionales")


class NotificationResponse(BaseModel):
    """Respuesta de notificación creada"""
    id: UUID
    user_id: UUID
    message: str
    status: str
    meta: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationStatus(BaseModel):
    """Estado de una notificación"""
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    meta: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class BatchNotificationRequest(BaseModel):
    """Solicitud para enviar múltiples notificaciones"""
    notifications: list[NotificationSendRequest] = Field(..., description="Lista de notificaciones a enviar")


class BatchNotificationResponse(BaseModel):
    """Respuesta de envío en lote"""
    results: list[Dict[str, Any]] = Field(..., description="Resultados del envío")


class SenderStats(BaseModel):
    """Estadísticas del servicio de envío"""
    total_notifications: int
    queued_notifications: int
    sent_notifications: int
    failed_notifications: int
    channel_stats: Dict[str, Dict[str, int]]

