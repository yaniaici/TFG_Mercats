from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import os
import structlog
import json
import asyncio

from database import get_db, Base, engine
from models import Notification, User
from schemas import (
    NotificationSendRequest,
    NotificationResponse,
    NotificationStatus,
    ChannelType
)
from adapters.webpush_adapter import WebPushAdapter
from adapters.android_adapter import AndroidAdapter
from adapters.ios_adapter import IOSAdapter
from notification_manager import NotificationManager

logger = structlog.get_logger()

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notification Sender Service",
    description="Servicio para enviar notificaciones a través de diferentes canales",
    version="0.1.0"
)

# CORS para permitir preflight OPTIONS desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar adapters
webpush_adapter = WebPushAdapter()
android_adapter = AndroidAdapter()
ios_adapter = IOSAdapter()

# Inicializar notification manager
notification_manager = NotificationManager(
    webpush_adapter=webpush_adapter,
    android_adapter=android_adapter,
    ios_adapter=ios_adapter
)

@app.get("/")
def root():
    return {
        "service": "notification-sender",
        "version": "0.1.0",
        "endpoints": {
            "send": "/send",
            "status": "/status/{notification_id}",
            "health": "/health",
        },
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: NotificationSendRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Envía una notificación a través del canal especificado
    """
    try:
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Crear notificación en la base de datos
        notification = Notification(
            user_id=request.user_id,
            message=request.message,
            status="queued",
            meta={
                "channel": request.channel.value,
                "title": request.title,
                "data": request.data or {}
            }
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Enviar notificación en background
        background_tasks.add_task(
            notification_manager.send_notification,
            notification_id=notification.id,
            user_id=request.user_id,
            message=request.message,
            title=request.title,
            channel=request.channel,
            data=request.data,
            db=db
        )

        return NotificationResponse.model_validate(notification)

    except Exception as e:
        logger.error("Error sending notification", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error enviando notificación: {str(e)}")

@app.get("/status/{notification_id}", response_model=NotificationStatus)
async def get_notification_status(
    notification_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de una notificación
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    return NotificationStatus(
        id=notification.id,
        status=notification.status,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
        meta=notification.meta or {}
    )

@app.post("/send-batch")
async def send_batch_notifications(
    requests: List[NotificationSendRequest],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Envía múltiples notificaciones en lote
    """
    results = []
    
    for request in requests:
        try:
            # Verificar que el usuario existe
            user = db.query(User).filter(User.id == request.user_id).first()
            if not user:
                results.append({
                    "user_id": str(request.user_id),
                    "status": "error",
                    "error": "Usuario no encontrado"
                })
                continue

            # Crear notificación
            notification = Notification(
                user_id=request.user_id,
                message=request.message,
                status="queued",
                meta={
                    "channel": request.channel.value,
                    "title": request.title,
                    "data": request.data or {}
                }
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)

            # Enviar en background
            background_tasks.add_task(
                notification_manager.send_notification,
                notification_id=notification.id,
                user_id=request.user_id,
                message=request.message,
                title=request.title,
                channel=request.channel,
                data=request.data,
                db=db
            )

            results.append({
                "notification_id": str(notification.id),
                "user_id": str(request.user_id),
                "status": "queued"
            })

        except Exception as e:
            results.append({
                "user_id": str(request.user_id),
                "status": "error",
                "error": str(e)
            })

    return {"results": results}

@app.get("/stats")
async def get_sender_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas del servicio de envío
    """
    total_notifications = db.query(Notification).count()
    queued_notifications = db.query(Notification).filter(Notification.status == "queued").count()
    sent_notifications = db.query(Notification).filter(Notification.status == "sent").count()
    failed_notifications = db.query(Notification).filter(Notification.status == "failed").count()

    # Estadísticas por canal
    channel_stats = {}
    notifications = db.query(Notification).all()
    
    for notification in notifications:
        channel = notification.meta.get("channel", "unknown") if notification.meta else "unknown"
        if channel not in channel_stats:
            channel_stats[channel] = {"total": 0, "sent": 0, "failed": 0, "queued": 0}
        
        channel_stats[channel]["total"] += 1
        if notification.status == "sent":
            channel_stats[channel]["sent"] += 1
        elif notification.status == "failed":
            channel_stats[channel]["failed"] += 1
        elif notification.status == "queued":
            channel_stats[channel]["queued"] += 1

    return {
        "total_notifications": total_notifications,
        "queued_notifications": queued_notifications,
        "sent_notifications": sent_notifications,
        "failed_notifications": failed_notifications,
        "channel_stats": channel_stats
    }

