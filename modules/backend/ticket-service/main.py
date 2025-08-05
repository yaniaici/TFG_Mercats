from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import uvicorn
from datetime import datetime

from database import get_db, engine
from models import Base, Ticket
from schemas import TicketResponse, TicketUploadResponse, TicketUpdate
from auth_client import auth_client
from utils import save_uploaded_file, get_mime_type
from config import settings

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Servicio de Tickets",
    description="Servicio para gestión de tickets de usuarios",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user_id(authorization: Optional[str] = Header(None)):
    """
    Dependency para obtener el ID del usuario actual desde el token
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido"
        )
    
    # Extraer token del header Authorization
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido"
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = await auth_client.verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    return user_id

@app.get("/")
async def root():
    return {
        "message": "Servicio de Tickets",
        "version": "1.0.0",
        "endpoints": {
            "upload_ticket": "/tickets/upload",
            "get_tickets": "/tickets",
            "get_ticket": "/tickets/{ticket_id}",
            "update_ticket": "/tickets/{ticket_id}",
            "delete_ticket": "/tickets/{ticket_id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# ========================================
# ENDPOINTS DE TICKETS
# ========================================

@app.post("/tickets/upload", response_model=TicketUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_ticket(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Subir un nuevo ticket (imagen)
    """
    try:
        # Guardar archivo
        file_path, filename, file_size = save_uploaded_file(file, current_user_id)
        
        # Obtener tipo MIME
        mime_type = get_mime_type(file.filename)
        
        # Crear registro en base de datos
        db_ticket = Ticket(
            user_id=current_user_id,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            status="pending"
        )
        
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        return TicketUploadResponse(
            message="Ticket subido exitosamente",
            ticket=db_ticket
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el ticket: {str(e)}"
        )

@app.get("/tickets", response_model=List[TicketResponse])
async def get_user_tickets(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Obtener todos los tickets del usuario actual
    """
    tickets = db.query(Ticket).filter(
        Ticket.user_id == current_user_id
    ).offset(skip).limit(limit).all()
    
    return tickets

@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Obtener un ticket específico del usuario actual
    """
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.user_id == current_user_id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    return ticket

@app.put("/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    ticket_update: TicketUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Actualizar un ticket específico del usuario actual
    """
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.user_id == current_user_id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    # Actualizar campos
    if ticket_update.status is not None:
        ticket.status = ticket_update.status
    if ticket_update.ticket_metadata is not None:
        ticket.ticket_metadata = ticket_update.ticket_metadata
    if ticket_update.processing_result is not None:
        ticket.processing_result = ticket_update.processing_result
    
    ticket.updated_at = datetime.now()
    db.commit()
    db.refresh(ticket)
    
    return ticket

@app.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Eliminar un ticket específico del usuario actual
    """
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.user_id == current_user_id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    # Eliminar archivo físico
    try:
        import os
        if os.path.exists(ticket.file_path):
            os.remove(ticket.file_path)
    except Exception as e:
        print(f"Error eliminando archivo físico: {e}")
    
    # Eliminar registro de base de datos
    db.delete(ticket)
    db.commit()
    
    return {"message": "Ticket eliminado exitosamente"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 