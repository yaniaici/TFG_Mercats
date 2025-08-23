from typing import Dict, Any, Optional
import structlog
import json
import os
from pywebpush import webpush, WebPushException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

logger = structlog.get_logger()


class WebPushAdapter:
    """
    Adapter para enviar notificaciones WebPush
    """
    
    def __init__(self):
        self.vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
        self.vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")
        self.vapid_email = os.getenv("VAPID_EMAIL", "noreply@mercat.com")
        
        if not self.vapid_private_key or not self.vapid_public_key:
            logger.warning("VAPID keys not configured, WebPush will not work")
    
    async def send_notification(
        self,
        subscription_data: Dict[str, Any],
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envía una notificación WebPush
        
        Args:
            subscription_data: Datos de suscripción del usuario (endpoint, keys, etc.)
            title: Título de la notificación
            message: Mensaje de la notificación
            data: Datos adicionales para la notificación
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            if not self.vapid_private_key or not self.vapid_public_key:
                return {
                    "success": False,
                    "error": "VAPID keys not configured"
                }
            
            # Preparar payload de la notificación
            payload = {
                "title": title,
                "body": message,
                "icon": "/icon-192x192.png",  # Icono por defecto
                "badge": "/badge-72x72.png",  # Badge por defecto
                "data": data or {}
            }
            
            # Configurar headers VAPID
            vapid_headers = {
                "vapid": {
                    "subject": f"mailto:{self.vapid_email}",
                    "public_key": self.vapid_public_key,
                    "private_key": self.vapid_private_key
                }
            }
            
            # Enviar notificación
            response = webpush(
                subscription_info=subscription_data,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=vapid_headers["vapid"]
            )
            
            logger.info(
                "WebPush notification sent successfully",
                status_code=response.status_code,
                title=title
            )
            
            return {
                "success": True,
                "delivery_info": {
                    "status_code": response.status_code,
                    "response_text": response.text,
                    "channel": "webpush"
                }
            }
            
        except WebPushException as e:
            logger.error(
                "WebPush error",
                error=str(e),
                status_code=getattr(e, 'status_code', None),
                response_text=getattr(e, 'response_text', None)
            )
            
            # Manejar diferentes tipos de errores
            if hasattr(e, 'status_code'):
                if e.status_code == 410:
                    # Suscripción expirada o inválida
                    return {
                        "success": False,
                        "error": "Subscription expired or invalid",
                        "should_remove_subscription": True
                    }
                elif e.status_code == 429:
                    # Rate limit
                    return {
                        "success": False,
                        "error": "Rate limit exceeded",
                        "should_retry": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"WebPush error: {e.status_code} - {e.response_text}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"WebPush error: {str(e)}"
                }
                
        except Exception as e:
            logger.error("Unexpected error in WebPush adapter", error=str(e))
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def validate_subscription(self, subscription_data: Dict[str, Any]) -> bool:
        """
        Valida que los datos de suscripción sean correctos
        
        Args:
            subscription_data: Datos de suscripción a validar
            
        Returns:
            True si la suscripción es válida, False en caso contrario
        """
        required_fields = ["endpoint", "keys"]
        if not all(field in subscription_data for field in required_fields):
            return False
        
        keys = subscription_data.get("keys", {})
        required_keys = ["p256dh", "auth"]
        if not all(key in keys for key in required_keys):
            return False
        
        return True
    
    def generate_vapid_keys(self) -> Dict[str, str]:
        """
        Genera un nuevo par de claves VAPID
        
        Returns:
            Dict con las claves pública y privada
        """
        try:
            private_key = ec.generate_private_key(ec.SECP256R1())
            public_key = private_key.public_key()
            
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            # Convertir a formato base64 URL safe para WebPush
            import base64
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import utils
            
            # Obtener coordenadas X e Y de la clave pública
            numbers = public_key.public_numbers()
            x = numbers.x
            y = numbers.y
            
            # Convertir a bytes
            x_bytes = x.to_bytes(32, 'big')
            y_bytes = y.to_bytes(32, 'big')
            
            # Concatenar y codificar en base64 URL safe
            raw_key = b'\x04' + x_bytes + y_bytes  # Prefijo 0x04 indica formato uncompressed
            public_key_b64 = base64.urlsafe_b64encode(raw_key).decode('utf-8').rstrip('=')
            
            return {
                "private_key": private_key_pem,
                "public_key": public_key_b64
            }
            
        except Exception as e:
            logger.error("Error generating VAPID keys", error=str(e))
            return {}


