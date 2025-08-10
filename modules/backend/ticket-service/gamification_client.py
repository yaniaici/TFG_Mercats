import requests
import uuid
from datetime import datetime
from typing import Optional
import structlog

logger = structlog.get_logger()

class GamificationClient:
    """Cliente para comunicarse con el servicio de gamificación"""
    
    def __init__(self, gamification_service_url: str = "http://gamification-service:8005"):
        self.gamification_service_url = gamification_service_url
    
    def process_ticket_event(self, user_id: uuid.UUID, ticket_id: uuid.UUID, 
                           is_valid: bool, total_amount: Optional[float] = None, 
                           store_name: Optional[str] = None) -> bool:
        """Envía un evento de ticket procesado al servicio de gamificación"""
        try:
            event_data = {
                "user_id": str(user_id),
                "ticket_id": str(ticket_id),
                "is_valid": is_valid,
                "total_amount": total_amount,
                "store_name": store_name,
                "processing_date": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.gamification_service_url}/events/ticket-processed",
                json=event_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Evento de gamificación enviado correctamente",
                           user_id=str(user_id),
                           ticket_id=str(ticket_id),
                           is_valid=is_valid)
                return True
            else:
                logger.warning("Error enviando evento de gamificación",
                              user_id=str(user_id),
                              ticket_id=str(ticket_id),
                              status_code=response.status_code,
                              response=response.text)
                return False
                
        except Exception as e:
            logger.error("Error comunicándose con el servicio de gamificación",
                        error=str(e),
                        user_id=str(user_id),
                        ticket_id=str(ticket_id))
            return False
    
    def get_user_stats(self, user_id: uuid.UUID) -> Optional[dict]:
        """Obtiene las estadísticas de gamificación del usuario"""
        try:
            response = requests.get(
                f"{self.gamification_service_url}/users/{user_id}/stats",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning("Error obteniendo estadísticas de gamificación",
                              user_id=str(user_id),
                              status_code=response.status_code)
                return None
                
        except Exception as e:
            logger.error("Error comunicándose con el servicio de gamificación",
                        error=str(e),
                        user_id=str(user_id))
            return None
    
    def get_gamification_service_health(self) -> bool:
        """Verifica la salud del servicio de gamificación"""
        try:
            response = requests.get(
                f"{self.gamification_service_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning("Servicio de gamificación no disponible", error=str(e))
            return False

def get_gamification_client() -> GamificationClient:
    """Función para obtener una instancia del cliente de gamificación"""
    return GamificationClient() 