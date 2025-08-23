import os
from typing import Optional

class Settings:
    """Configuración centralizada del servicio de tickets"""
    
    # Configuración de la base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ticket_user:ticket_password@postgres:5432/ticket_analytics"
    )
    
    # Configuración del servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8003"))  # Puerto específico para ticket-service
    
    # Configuración de CORS
    ALLOWED_ORIGINS: list = ["*"]  # En producción, especificar dominios específicos
    
    # Configuración de archivos
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png"]
    
    # Configuración de autenticación
    AUTH_SERVICE_URL: str = os.getenv(
        "AUTH_SERVICE_URL", 
        "http://auth-service:8001"
    )
    
    # Configuración de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configuración de detección de duplicados
    ENABLE_DUPLICATE_DETECTION: bool = os.getenv("ENABLE_DUPLICATE_DETECTION", "true").lower() == "true"

# Instancia global de configuración
settings = Settings() 