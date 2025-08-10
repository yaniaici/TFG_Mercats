from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv(
    "GAMIFICATION_DATABASE_URL",
    "postgresql://ticket_user:ticket_password@postgres:5432/ticket_analytics"
)

# Crear engine de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

def get_db():
    """Función para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 