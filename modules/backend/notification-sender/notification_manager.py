from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from uuid import UUID
import structlog
from datetime import datetime

from models import Notification, UserSubscription
from schemas import ChannelType
from adapters.webpush_adapter import WebPushAdapter
from adapters.android_adapter import AndroidAdapter
from adapters.ios_adapter import IOSAdapter

logger = structlog.get_logger()


class NotificationManager:
    """
    Manager que coordina el envío de notificaciones a través de diferentes canales
    """
    
    def __init__(
        self,
        webpush_adapter: WebPushAdapter,
        android_adapter: AndroidAdapter,
        ios_adapter: IOSAdapter
    ):
        self.webpush_adapter = webpush_adapter
        self.android_adapter = android_adapter
        self.ios_adapter = ios_adapter
        
        # Mapeo de canales a adapters
        self.channel_adapters = {
            ChannelType.WEBPUSH: self.webpush_adapter,
            ChannelType.ANDROID: self.android_adapter,
            ChannelType.IOS: self.ios_adapter
        }
    
    async def send_notification(
        self,
        notification_id: UUID,
        user_id: UUID,
        message: str,
        title: str,
        channel: ChannelType,
        data: Optional[Dict[str, Any]] = None,
        db: Session = None
    ):
        """
        Envía una notificación a través del canal especificado
        """
        try:
            logger.info(
                "Sending notification",
                notification_id=str(notification_id),
                user_id=str(user_id),
                channel=channel.value
            )
            
            # Obtener el adapter correspondiente
            adapter = self.channel_adapters.get(channel)
            if not adapter:
                await self._mark_notification_failed(
                    notification_id, 
                    f"Canal no soportado: {channel.value}",
                    db
                )
                return
            
            # Obtener suscripción del usuario para este canal
            subscription = self._get_user_subscription(user_id, channel, db)
            if not subscription:
                await self._mark_notification_failed(
                    notification_id,
                    f"Usuario no tiene suscripción para el canal {channel.value}",
                    db
                )
                return
            
            # Enviar notificación a través del adapter
            result = await adapter.send_notification(
                subscription_data=subscription.subscription_data,
                title=title,
                message=message,
                data=data or {}
            )
            
            if result.get("success"):
                await self._mark_notification_sent(
                    notification_id,
                    result.get("delivery_info", {}),
                    db
                )
                logger.info(
                    "Notification sent successfully",
                    notification_id=str(notification_id),
                    channel=channel.value
                )
            else:
                await self._mark_notification_failed(
                    notification_id,
                    result.get("error", "Error desconocido"),
                    db
                )
                logger.error(
                    "Failed to send notification",
                    notification_id=str(notification_id),
                    error=result.get("error"),
                    channel=channel.value
                )
                
        except Exception as e:
            logger.error(
                "Error in notification manager",
                notification_id=str(notification_id),
                error=str(e)
            )
            await self._mark_notification_failed(
                notification_id,
                str(e),
                db
            )
    
    def _get_user_subscription(
        self,
        user_id: UUID,
        channel: ChannelType,
        db: Session
    ) -> Optional[UserSubscription]:
        """
        Obtiene la suscripción activa del usuario para un canal específico
        """
        return db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.channel == channel.value,
            UserSubscription.is_active == True
        ).first()
    
    async def _mark_notification_sent(
        self,
        notification_id: UUID,
        delivery_info: Dict[str, Any],
        db: Session
    ):
        """
        Marca una notificación como enviada
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            notification.status = "sent"
            notification.meta = {
                **(notification.meta or {}),
                "delivery_info": delivery_info,
                "sent_at": datetime.utcnow().isoformat()
            }
            db.commit()
    
    async def _mark_notification_failed(
        self,
        notification_id: UUID,
        error_message: str,
        db: Session
    ):
        """
        Marca una notificación como fallida
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            notification.status = "failed"
            notification.meta = {
                **(notification.meta or {}),
                "error": error_message,
                "failed_at": datetime.utcnow().isoformat()
            }
            db.commit()
    
    async def send_batch_notifications(
        self,
        notifications: list[Dict[str, Any]],
        db: Session
    ):
        """
        Envía múltiples notificaciones en lote
        """
        results = []
        
        for notification_data in notifications:
            try:
                await self.send_notification(
                    notification_id=notification_data["notification_id"],
                    user_id=notification_data["user_id"],
                    message=notification_data["message"],
                    title=notification_data["title"],
                    channel=notification_data["channel"],
                    data=notification_data.get("data"),
                    db=db
                )
                results.append({
                    "notification_id": str(notification_data["notification_id"]),
                    "status": "processed"
                })
            except Exception as e:
                results.append({
                    "notification_id": str(notification_data["notification_id"]),
                    "status": "error",
                    "error": str(e)
                })
        
        return results

