import os
from typing import Optional

class Settings:
    """Configuración centralizada del servicio de autenticación"""
    
    # Configuración de la base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ticket_user:ticket_password@localhost:5432/ticket_analytics"
    )
    
    # Configuración de seguridad
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "tu_clave_secreta_super_segura_cambiar_en_produccion"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas fijo
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30 días
    
    # Configuración del servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))  # Puerto diferente al main-backend
    
    # Configuración de CORS
    ALLOWED_ORIGINS: list = ["*"]  # En producción, especificar dominios específicos
    
    # Configuración de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# Instancia global de configuración
settings = Settings() 