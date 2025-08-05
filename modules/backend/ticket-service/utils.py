import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, status, UploadFile
from config import settings
import mimetypes

def validate_file_extension(filename: str) -> bool:
    """
    Validar que el archivo tenga una extensión permitida
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        bool: True si la extensión es válida
    """
    file_extension = Path(filename).suffix.lower()
    return file_extension in settings.ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """
    Validar que el tamaño del archivo no exceda el límite
    
    Args:
        file_size: Tamaño del archivo en bytes
        
    Returns:
        bool: True si el tamaño es válido
    """
    return file_size <= settings.MAX_FILE_SIZE

def generate_unique_filename(original_filename: str) -> str:
    """
    Generar un nombre único para el archivo
    
    Args:
        original_filename: Nombre original del archivo
        
    Returns:
        str: Nombre único generado
    """
    file_extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"

def ensure_upload_directory() -> str:
    """
    Asegurar que el directorio de uploads existe
    
    Returns:
        str: Ruta del directorio de uploads
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return str(upload_dir)

def save_uploaded_file(file: UploadFile, user_id: str) -> tuple[str, str, int]:
    """
    Guardar un archivo subido
    
    Args:
        file: Archivo subido
        user_id: ID del usuario
        
    Returns:
        tuple: (file_path, filename, file_size)
    """
    # Validar extensión
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión de archivo no permitida. Permitidas: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Leer contenido del archivo
    content = file.file.read()
    file_size = len(content)
    
    # Validar tamaño
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo demasiado grande. Máximo: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Generar nombre único
    filename = generate_unique_filename(file.filename)
    
    # Crear directorio de usuario si no existe
    upload_dir = ensure_upload_directory()
    user_dir = Path(upload_dir) / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar archivo
    file_path = user_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)
    
    return str(file_path), filename, file_size

def get_mime_type(filename: str) -> str:
    """
    Obtener el tipo MIME del archivo
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        str: Tipo MIME
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream" 