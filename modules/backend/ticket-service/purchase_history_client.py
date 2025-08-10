#!/usr/bin/env python3
"""
Cliente para comunicarse con el auth-service para actualizar el historial de compras
"""

import requests
import structlog
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

logger = structlog.get_logger()

class PurchaseHistoryClient:
    def __init__(self, auth_service_url: str = "http://auth-service:8001"):
        """
        Inicializar cliente de historial de compras
        
        Args:
            auth_service_url: URL del servicio de autenticación
        """
        self.auth_service_url = auth_service_url
        self.base_url = f"{auth_service_url}/purchase-history"
        
        print(f"🛒 Inicializando Purchase History Client...")
        print(f"   📡 Auth Service URL: {auth_service_url}")
    
    def create_purchase_record(self, purchase_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crear un nuevo registro de compra en el historial del usuario
        
        Args:
            purchase_data: Datos de la compra a registrar
            
        Returns:
            Dict con la respuesta del servicio o None si hay error
        """
        try:
            # Preparar los datos para el auth-service
            payload = {
                "user_id": str(purchase_data["user_id"]),
                "ticket_id": str(purchase_data["ticket_id"]),
                "purchase_date": purchase_data["purchase_date"].isoformat(),
                "store_name": purchase_data["store_name"],
                "total_amount": purchase_data["total_amount"],
                "products": purchase_data["products"],
                "num_products": purchase_data["num_products"],
                "ticket_type": purchase_data.get("ticket_type"),
                "is_market_store": purchase_data.get("is_market_store", False)
            }
            
            print(f"   📝 Creando registro de compra para usuario {purchase_data['user_id']}")
            print(f"      🏪 Tienda: {purchase_data['store_name']}")
            print(f"      💰 Total: {purchase_data['total_amount']}€")
            print(f"      📦 Productos: {purchase_data['num_products']}")
            
            response = requests.post(
                f"{self.auth_service_url}/purchase-history/create",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"      ✅ Registro de compra creado exitosamente")
                logger.info("Registro de compra creado", 
                           user_id=str(purchase_data["user_id"]),
                           ticket_id=str(purchase_data["ticket_id"]),
                           store_name=purchase_data["store_name"])
                return result
            else:
                error_msg = f"Error creando registro de compra: {response.status_code} - {response.text}"
                print(f"      ❌ {error_msg}")
                logger.error("Error creando registro de compra", 
                            error=error_msg,
                            user_id=str(purchase_data["user_id"]),
                            ticket_id=str(purchase_data["ticket_id"]))
                return None
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con auth-service: {str(e)}"
            print(f"      💥 {error_msg}")
            logger.error("Error de conexión con auth-service", 
                        error=str(e),
                        user_id=str(purchase_data["user_id"]),
                        ticket_id=str(purchase_data["ticket_id"]))
            return None
        except Exception as e:
            error_msg = f"Error inesperado creando registro de compra: {str(e)}"
            print(f"      💥 {error_msg}")
            logger.error("Error inesperado creando registro de compra", 
                        error=str(e),
                        user_id=str(purchase_data["user_id"]),
                        ticket_id=str(purchase_data["ticket_id"]))
            return None
    
    def check_purchase_exists(self, ticket_id: uuid.UUID) -> bool:
        """
        Verificar si ya existe un registro de compra para un ticket específico
        
        Args:
            ticket_id: ID del ticket a verificar
            
        Returns:
            True si existe, False si no
        """
        try:
            response = requests.get(
                f"{self.auth_service_url}/purchase-history/ticket/{ticket_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('exists', False)
            else:
                return False
            
        except Exception as e:
            logger.warning("Error verificando existencia de compra", 
                          error=str(e),
                          ticket_id=str(ticket_id))
            return False
    
    def get_auth_service_health(self) -> bool:
        """
        Verificar que el auth-service esté disponible
        
        Returns:
            True si está disponible, False si no
        """
        try:
            response = requests.get(f"{self.auth_service_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning("Auth service no disponible", error=str(e))
            return False

# Instancia global
purchase_history_client = None

def get_purchase_history_client() -> PurchaseHistoryClient:
    """Obtener instancia del cliente de historial de compras"""
    global purchase_history_client
    if purchase_history_client is None:
        purchase_history_client = PurchaseHistoryClient()
    return purchase_history_client 