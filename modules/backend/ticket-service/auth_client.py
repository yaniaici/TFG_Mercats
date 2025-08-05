import httpx
from fastapi import HTTPException, status
from config import settings
from typing import Optional

class AuthClient:
    """Cliente para comunicarse con el servicio de autenticación"""
    
    def __init__(self):
        self.base_url = settings.AUTH_SERVICE_URL
    
    async def verify_token(self, token: str) -> Optional[str]:
        """
        Verificar un token JWT con el servicio de autenticación
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            user_id: ID del usuario si el token es válido
            None: Si el token es inválido
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/verify",
                    json={"token": token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("user_id")
                else:
                    return None
                    
        except Exception as e:
            print(f"Error verificando token: {e}")
            return None
    
    async def get_user_info(self, token: str) -> Optional[dict]:
        """
        Obtener información del usuario desde el servicio de autenticación
        
        Args:
            token: Token JWT del usuario
            
        Returns:
            user_info: Información del usuario si el token es válido
            None: Si el token es inválido
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            print(f"Error obteniendo información del usuario: {e}")
            return None

# Instancia global del cliente de autenticación
auth_client = AuthClient() 