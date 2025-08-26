from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import shutil
from datetime import datetime, timedelta

from database import get_db
from models import Ticket, MarketStore
from schemas import (
    TicketCreate, TicketResponse, TicketUploadResponse, 
    MarketStoreCreate, MarketStoreResponse, MarketStoreUpdate,
    TicketProcessingResult
)
from market_store_service import MarketStoreService
from purchase_history_client import get_purchase_history_client
from gamification_client import get_gamification_client
from config import settings
# Configuración del AI Ticket Processor
AI_PROCESSOR_URL = "http://ai-ticket-processor:8004"
AI_AVAILABLE = True
print("✅ AI system disponible via HTTP")

app = FastAPI(title="Ticket Service API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de archivos
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Inicializar servicios
market_store_service = None
ai_processor = None

def get_market_store_service(db: Session = Depends(get_db)):
    global market_store_service
    if market_store_service is None:
        market_store_service = MarketStoreService(db)
    return market_store_service

import requests

def process_ticket_with_ai(file_path: str, market_service) -> dict:
    """Procesar ticket usando el AI Ticket Processor via HTTP"""
    try:
        # Leer el archivo y convertirlo a base64
        import base64
        with open(file_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Preparar datos para el AI processor
        payload = {
            "image_base64": image_data,
            "market_stores": market_service.get_market_store_names()
        }
        
        # Llamar al AI Ticket Processor
        response = requests.post(
            f"{AI_PROCESSOR_URL}/process-ticket-api",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return {
                "error": f"AI processor error: {response.status_code}",
                "ticket_status": "failed",
                "procesado_correctamente": False
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "ticket_status": "failed",
            "procesado_correctamente": False
        }

def update_purchase_history(ticket: Ticket, processing_result: dict) -> bool:
    """
    Actualizar el historial de compras cuando se procesa un ticket válido
    
    Args:
        ticket: Objeto Ticket procesado
        processing_result: Resultado del procesamiento de IA
        
    Returns:
        True si se actualizó correctamente, False si no
    """
    try:
        # Solo actualizar si el ticket fue procesado correctamente y es válido
        if not processing_result.get('procesado_correctamente', False):
            print(f"   ⏭️ Ticket no procesado correctamente, saltando historial de compras")
            return False
        
        # Verificar que tenemos los datos necesarios (solo tienda es obligatoria)
        if not processing_result.get('tienda'):
            print(f"   ⏭️ Datos insuficientes para historial de compras: falta tienda")
            return False
        
        # Obtener cliente de historial de compras
        purchase_client = get_purchase_history_client()
        
        # Verificar si ya existe un registro para este ticket
        if purchase_client.check_purchase_exists(ticket.id):
            print(f"   ⏭️ Ya existe registro de compra para este ticket")
            return False
        
        # Preparar datos de la compra
        purchase_date = datetime.now()
        if processing_result.get('fecha'):
            try:
                # Intentar parsear la fecha del ticket
                date_str = processing_result['fecha']
                if ':' in date_str:  # Si incluye hora
                    purchase_date = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
                else:  # Solo fecha
                    purchase_date = datetime.strptime(date_str, "%d/%m/%Y")
            except:
                # Si falla el parsing, usar fecha actual
                purchase_date = datetime.now()
        
        # Procesar total - usar 0 si está vacío o nulo
        total_amount = 0.0
        if processing_result.get('total'):
            try:
                total_amount = float(processing_result['total'])
            except (ValueError, TypeError):
                total_amount = 0.0
        
        purchase_data = {
            "user_id": ticket.user_id,
            "ticket_id": ticket.id,
            "purchase_date": purchase_date,
            "store_name": processing_result['tienda'],
            "total_amount": total_amount,
            "products": processing_result.get('productos', []),
            "num_products": processing_result.get('num_productos', 0),
            "ticket_type": processing_result.get('tipo_ticket'),
            "is_market_store": processing_result.get('es_tienda_mercado', False)
        }
        
        # Crear registro de compra
        result = purchase_client.create_purchase_record(purchase_data)
        
        if result:
            print(f"   ✅ Historial de compras actualizado para usuario {ticket.user_id}")
            return True
        else:
            print(f"   ❌ Error actualizando historial de compras")
            return False
            
    except Exception as e:
        print(f"   💥 Error en actualización de historial de compras: {str(e)}")
        return False

def check_duplicate_ticket(processing_result: dict, user_id: uuid.UUID, db: Session) -> bool:
    """
    Verificar si existe un ticket duplicado basado en fecha, hora y productos
    
    Args:
        processing_result: Resultado del procesamiento de IA
        user_id: ID del usuario
        db: Sesión de base de datos
        
    Returns:
        True si es un duplicado, False si no
    """
    # Verificar si la detección de duplicados está habilitada
    if not settings.ENABLE_DUPLICATE_DETECTION:
        print("   ℹ️  Detección de duplicados deshabilitada por configuración")
        return False
        
    print(f"   🔍 Verificando duplicados para usuario {user_id}")
    
    try:
        # Obtener fecha y hora del ticket actual
        fecha_str = processing_result.get('fecha', '')
        if not fecha_str:
            print("   ❌ No se encontró fecha en el processing_result")
            return False
        
        print(f"   📅 Fecha del ticket actual: {fecha_str}")
        print(f"   🛒 Productos del ticket actual: {len(processing_result.get('productos', []))}")
        
        # Parsear fecha y hora del ticket actual
        try:
            if ':' in fecha_str:  # Si incluye hora
                purchase_datetime = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
            else:  # Solo fecha
                purchase_datetime = datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError as e:
            print(f"   ❌ Error parseando fecha del ticket actual: {e}")
            return False
        
        # Obtener productos del ticket actual
        productos = processing_result.get('productos', [])
        if not productos:
            print("   ❌ No se encontraron productos en el processing_result")
            return False
        
        # Normalizar productos para comparación (ordenar campos)
        def normalize_product(product):
            if isinstance(product, dict):
                # Ordenar campos: nombre, cantidad, precio
                return {
                    'nombre': str(product.get('nombre', '')),
                    'cantidad': str(product.get('cantidad', '')),
                    'precio': str(product.get('precio', ''))
                }
            return product
        
        productos_normalized = [normalize_product(p) for p in productos]
        productos_sorted = sorted([str(p) for p in productos_normalized])
        productos_hash = hash(tuple(productos_sorted))
        print(f"   🛒 Productos del ticket actual (normalizados): {productos_sorted[:3]}...")  # Mostrar solo los primeros 3
        print(f"   🛒 Hash de productos del ticket actual: {productos_hash}")
        
        # Buscar tickets del mismo usuario que ya han sido procesados
        existing_tickets = db.query(Ticket).filter(
            Ticket.user_id == user_id,
            Ticket.status.in_(['done_approved', 'done_rejected', 'duplicate']),
            Ticket.processing_result.isnot(None)
        ).all()
        
        print(f"   🔍 Encontrados {len(existing_tickets)} tickets procesados para comparar")
        
        # Verificar cada ticket existente
        for existing_ticket in existing_tickets:
            existing_result = existing_ticket.processing_result or {}
            existing_productos = existing_result.get('productos', [])
            existing_fecha = existing_result.get('fecha', '')
            
            print(f"   🔍 Comparando con ticket {existing_ticket.id} - fecha: {existing_fecha}, productos: {len(existing_productos)}")
            
            # Verificar que tenga productos y fecha
            if existing_productos and existing_fecha:
                try:
                    # Parsear fecha del ticket existente
                    if ':' in existing_fecha:
                        existing_datetime = datetime.strptime(existing_fecha, "%d/%m/%Y %H:%M")
                    else:
                        existing_datetime = datetime.strptime(existing_fecha, "%d/%m/%Y")
                    
                    # Verificar si está en la ventana de tiempo (±5 minutos)
                    time_window_start = purchase_datetime - timedelta(minutes=5)
                    time_window_end = purchase_datetime + timedelta(minutes=5)
                    
                    print(f"   ⏰ Ventana de tiempo: {time_window_start} a {time_window_end}")
                    print(f"   ⏰ Fecha del ticket existente: {existing_datetime}")
                    
                    if time_window_start <= existing_datetime <= time_window_end:
                        print(f"   ⏰ Coincidencia de fecha encontrada: {existing_fecha} está en ventana de ±5 minutos")
                        # Verificar si los productos coinciden
                        existing_productos_normalized = [normalize_product(p) for p in existing_productos]
                        existing_productos_sorted = sorted([str(p) for p in existing_productos_normalized])
                        existing_productos_hash = hash(tuple(existing_productos_sorted))
                        
                        print(f"   🛒 Productos del ticket existente (normalizados): {existing_productos_sorted[:3]}...")  # Mostrar solo los primeros 3
                        print(f"   🛒 Comparando hashes: actual={productos_hash}, existente={existing_productos_hash}")
                        
                        # Comparación directa de productos (más robusta)
                        productos_actual_set = set(str(p) for p in productos_normalized)
                        productos_existente_set = set(str(p) for p in existing_productos_normalized)
                        
                        print(f"   🛒 Comparación directa: {len(productos_actual_set)} vs {len(productos_existente_set)} productos únicos")
                        
                        if existing_productos_hash == productos_hash:
                            print(f"   🔍 Duplicado encontrado (hash): fecha={existing_fecha}, productos={len(existing_productos)}")
                            return True
                        elif productos_actual_set == productos_existente_set:
                            print(f"   🔍 Duplicado encontrado (comparación directa): fecha={existing_fecha}, productos={len(existing_productos)}")
                            return True
                        else:
                            print(f"   ❌ Productos no coinciden (hash ni comparación directa)")
                            # Mostrar diferencias para debug
                            diff_actual = productos_actual_set - productos_existente_set
                            diff_existente = productos_existente_set - productos_actual_set
                            if diff_actual:
                                print(f"   🔍 Productos solo en actual: {list(diff_actual)[:2]}...")
                            if diff_existente:
                                print(f"   🔍 Productos solo en existente: {list(diff_existente)[:2]}...")
                    else:
                        print(f"   ⏰ Fecha fuera de la ventana de tiempo")
                except ValueError as e:
                    print(f"   ❌ Error parseando fecha del ticket existente: {e}")
                    continue
            else:
                print(f"   ❌ Ticket existente no tiene productos o fecha válidos")
        
        print(f"   ✅ No se encontraron duplicados")
        return False
        
    except Exception as e:
        print(f"   ❌ Error verificando duplicados: {e}")
        return False

def update_gamification(ticket: Ticket, processing_result: dict) -> bool:
    """
    Actualizar la gamificación cuando se procesa un ticket
    
    Args:
        ticket: Objeto Ticket procesado
        processing_result: Resultado del procesamiento de IA
        
    Returns:
        True si se actualizó correctamente, False si no
    """
    try:
        # Determinar si el ticket es válido (debe ser procesado correctamente, tener tienda y ser tienda del mercado)
        is_valid = (
            processing_result.get('procesado_correctamente', False) and 
            processing_result.get('tienda') and 
            processing_result.get('es_tienda_mercado', False)
        )
        
        # Procesar total para gamificación
        total_amount = None
        if processing_result.get('total'):
            try:
                total_amount = float(processing_result['total'])
            except (ValueError, TypeError):
                total_amount = None
        
        # Obtener cliente de gamificación
        gamification_client = get_gamification_client()
        
        # Enviar evento de gamificación
        result = gamification_client.process_ticket_event(
            user_id=ticket.user_id,
            ticket_id=ticket.id,
            is_valid=is_valid,
            total_amount=total_amount,
            store_name=processing_result.get('tienda')
        )
        
        if result:
            print(f"   🎮 Gamificación actualizada para usuario {ticket.user_id}")
            return True
        else:
            print(f"   ⚠️ Error actualizando gamificación")
            return False
            
    except Exception as e:
        print(f"   💥 Error en actualización de gamificación: {str(e)}")
        return False

# Endpoints para Market Stores
@app.post("/market-stores/", response_model=MarketStoreResponse)
def create_market_store(
    market_store: MarketStoreCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva tienda del mercado"""
    service = MarketStoreService(db)
    return service.create_market_store(market_store)

@app.get("/market-stores/", response_model=List[MarketStoreResponse])
def get_market_stores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todas las tiendas del mercado"""
    service = MarketStoreService(db)
    return service.get_all_market_stores(skip=skip, limit=limit)

@app.get("/market-stores/{market_store_id}", response_model=MarketStoreResponse)
def get_market_store(
    market_store_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Obtener una tienda del mercado por ID"""
    service = MarketStoreService(db)
    market_store = service.get_market_store(market_store_id)
    if not market_store:
        raise HTTPException(status_code=404, detail="Tienda del mercado no encontrada")
    return market_store

@app.put("/market-stores/{market_store_id}", response_model=MarketStoreResponse)
def update_market_store(
    market_store_id: uuid.UUID,
    market_store: MarketStoreUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una tienda del mercado"""
    service = MarketStoreService(db)
    updated_store = service.update_market_store(market_store_id, market_store)
    if not updated_store:
        raise HTTPException(status_code=404, detail="Tienda del mercado no encontrada")
    return updated_store

@app.delete("/market-stores/{market_store_id}")
def delete_market_store(
    market_store_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Eliminar una tienda del mercado"""
    service = MarketStoreService(db)
    success = service.delete_market_store(market_store_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tienda del mercado no encontrada")
    return {"message": "Tienda del mercado eliminada correctamente"}

@app.get("/market-stores/verify/{store_name}")
def verify_market_store(store_name: str, db: Session = Depends(get_db)):
    """Verificar si una tienda es del mercado"""
    service = MarketStoreService(db)
    is_market_store = service.is_market_store(store_name)
    return {
        "store_name": store_name,
        "is_market_store": is_market_store
    }

# Endpoints para Tickets (actualizados)
@app.post("/tickets/upload/", response_model=TicketUploadResponse)
async def upload_ticket(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Subir un nuevo ticket"""
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        # Generar nombre único
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Calcular tamaño real del archivo guardado
        try:
            saved_file_size = os.path.getsize(file_path)
        except Exception:
            saved_file_size = 0
        
        # Crear registro en base de datos
        ticket_data = TicketCreate(
            original_filename=file.filename,
            ticket_metadata={
                "file_size": saved_file_size,
                "mime_type": file.content_type,
                "upload_timestamp": datetime.now().isoformat()
            }
        )
        
        db_ticket = Ticket(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            filename=unique_filename,
            original_filename=ticket_data.original_filename,
            file_path=file_path,
            file_size=saved_file_size,
            mime_type=file.content_type,
            ticket_metadata=ticket_data.ticket_metadata,
            status="pending"
        )
        
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        return TicketUploadResponse(
            message="Ticket subido correctamente",
            ticket=TicketResponse.from_orm(db_ticket)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo ticket: {str(e)}")

@app.post("/tickets/digital/", response_model=TicketResponse)
@app.post("/digital/", response_model=TicketResponse)
async def create_digital_ticket(
    ticket_data: dict,
    db: Session = Depends(get_db)
):
    """Crear un ticket digital desde el componente SendTicket"""
    try:
        # Extraer datos del ticket
        user_id = ticket_data.get('user_id')
        store_name = ticket_data.get('store_name')
        total_amount = ticket_data.get('total_amount', 0)
        products = ticket_data.get('products', [])
        purchase_date = ticket_data.get('purchase_date')
        
        if not user_id or not store_name:
            raise HTTPException(
                status_code=400, 
                detail="user_id y store_name son obligatorios"
            )
        
        # Crear ticket digital
        db_ticket = Ticket(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            filename=f"digital_ticket_{uuid.uuid4()}.json",
            original_filename=f"Ticket Digital - {store_name}",
            file_path="",  # No hay archivo físico
            file_size=0,
            mime_type="application/json",
            ticket_metadata={
                "type": "digital",
                "store_name": store_name,
                "total_amount": total_amount,
                "products": products,
                "purchase_date": purchase_date,
                "created_by": "vendor"
            },
            status="done_approved"  # Los tickets digitales se aprueban automáticamente
        )
        
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        # Actualizar historial de compras
        try:
            purchase_history_client = get_purchase_history_client()
            purchase_data = {
                "user_id": user_id,
                "ticket_id": str(db_ticket.id),
                "purchase_date": datetime.now(),
                "store_name": store_name,
                "total_amount": total_amount,
                "products": products,
                "num_products": len(products),
                "ticket_type": "digital",
                "is_market_store": True  # Los tickets digitales se consideran del mercado
            }
            purchase_history_client.create_purchase_record(purchase_data)
        except Exception as e:
            print(f"Error actualizando historial de compras: {e}")
        
        # Actualizar gamificación
        try:
            gamification_client = get_gamification_client()
            gamification_client.process_ticket_event(
                user_id=uuid.UUID(user_id),
                ticket_id=db_ticket.id,
                is_valid=True,
                total_amount=total_amount,
                store_name=store_name
            )
        except Exception as e:
            print(f"Error actualizando gamificación: {e}")
        
        return TicketResponse.from_orm(db_ticket)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error creando ticket digital: {str(e)}"
        )

@app.get("/tickets/all/", response_model=List[TicketResponse])
def get_all_tickets(
    user_id: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todos los tickets (incluyendo rechazados) para la sección de estado"""
    query = db.query(Ticket)
    
    if user_id:
        query = query.filter(Ticket.user_id == uuid.UUID(user_id))
    
    if status:
        query = query.filter(Ticket.status == status)
    
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return [TicketResponse.from_orm(ticket).to_response_dict() for ticket in tickets]

@app.get("/tickets/")
def get_tickets(
    user_id: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener tickets aprobados y digitales para el dashboard"""
    query = db.query(Ticket)
    
    if user_id:
        query = query.filter(Ticket.user_id == uuid.UUID(user_id))
    
    # Filtrar solo tickets aprobados y digitales para el dashboard
    if status:
        query = query.filter(Ticket.status == status)
    else:
        # Por defecto, mostrar solo aprobados y digitales
        query = query.filter(
            (Ticket.status == "done_approved") | 
            (Ticket.ticket_metadata.contains({"type": "digital"})) |
            (Ticket.original_filename.like("Ticket Digital%"))
        )
    
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    response_tickets = []
    for ticket in tickets:
        ticket_response = TicketResponse.from_orm(ticket)
        response_dict = ticket_response.dict()
        
        # Calcular propiedades computadas directamente
        print(f"DEBUG: Ticket {ticket.id} - ticket_metadata: {response_dict.get('ticket_metadata')}")
        
        if response_dict.get('ticket_metadata', {}).get("type") == "digital":
            store_name = response_dict['ticket_metadata'].get("store_name", "Ticket Digital")
            response_dict['display_name'] = f"Ticket Digital - {store_name}"
            response_dict['store_name'] = response_dict['ticket_metadata'].get("store_name", "Tienda Digital")
            response_dict['total_amount'] = response_dict['ticket_metadata'].get("total_amount", 0.0)
            response_dict['products'] = response_dict['ticket_metadata'].get("products", [])
            response_dict['is_digital'] = True
            print(f"DEBUG: Ticket {ticket.id} - Es digital, display_name: {response_dict.get('display_name')}")
        else:
            store_name = response_dict.get('processing_result', {}).get("tienda", "Tienda del Mercat")
            response_dict['display_name'] = f"Compra - {store_name}"
            response_dict['store_name'] = response_dict.get('processing_result', {}).get("tienda", "Desconocida")
            response_dict['total_amount'] = response_dict.get('processing_result', {}).get("total", 0.0)
            response_dict['products'] = response_dict.get('processing_result', {}).get("productos", [])
            response_dict['is_digital'] = False
            print(f"DEBUG: Ticket {ticket.id} - Es escaneado, display_name: {response_dict.get('display_name')}")
        
        print(f"DEBUG: Ticket {ticket.id} - Final response_dict keys: {list(response_dict.keys())}")
        response_tickets.append(response_dict)
    return response_tickets

@app.get("/tickets/pending/", response_model=List[dict])
def get_pending_tickets(db: Session = Depends(get_db)):
    """Obtener todos los tickets pendientes de procesamiento con imagen en base64"""
    tickets = db.query(Ticket).filter(Ticket.status == "pending").all()
    
    result = []
    for ticket in tickets:
        ticket_data = TicketResponse.from_orm(ticket).dict()
        
        # Leer la imagen y convertirla a base64
        try:
            import base64
            with open(ticket.file_path, 'rb') as file:
                image_data = file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                ticket_data['image_base64'] = image_base64
        except Exception as e:
            print(f"Error leyendo imagen para ticket {ticket.id}: {str(e)}")
            ticket_data['image_base64'] = None
        
        result.append(ticket_data)
    
    return result

@app.post("/tickets/{ticket_id}/process/")
def process_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Procesar un ticket específico con IA"""
    try:
        # Obtener ticket
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")
        
        if ticket.status != "pending":
            raise HTTPException(status_code=400, detail="Ticket ya procesado")
        
        # Si el ticket ya tiene processing_result, significa que ya fue procesado por IA
        # y posiblemente marcado como duplicado
        if ticket.processing_result and ticket.status == "duplicate":
            return {
                "message": "Ticket ya marcado como duplicado",
                "ticket": TicketResponse.from_orm(ticket),
                "processing_result": ticket.processing_result
            }
        
        if not AI_AVAILABLE:
            raise HTTPException(status_code=503, detail="AI system no disponible")
        
        # Si el ticket ya tiene processing_result, usarlo en lugar de procesar de nuevo
        if ticket.processing_result:
            result = ticket.processing_result
        else:
            # Procesar con IA via HTTP
            market_service = get_market_store_service(db)
            result = process_ticket_with_ai(ticket.file_path, market_service)
        
        # Verificar si es un ticket duplicado
        if result.get('procesado_correctamente', False):
            is_duplicate = check_duplicate_ticket(result, ticket.user_id, db)
            if is_duplicate:
                # Marcar como duplicado
                result['ticket_status'] = 'duplicate'
                result['status_message'] = 'Ticket duplicado detectado'
                result['duplicate_detected'] = True
                print(f"   ⚠️ Ticket duplicado detectado para usuario {ticket.user_id}")
        
        # Actualizar ticket
        ticket.status = result.get('ticket_status', 'failed')
        ticket.processing_result = result
        ticket.updated_at = datetime.now()
        
        db.commit()
        db.refresh(ticket)
        
        # Solo actualizar historial de compras si el ticket fue procesado correctamente y no es duplicado
        if result.get('ticket_status') in ['done_approved', 'done_rejected'] and not result.get('duplicate_detected', False):
            update_purchase_history(ticket, result)
        
        # Actualizar gamificación para todos los tickets procesados (excepto duplicados)
        if not result.get('duplicate_detected', False):
            update_gamification(ticket, result)
        
        return {
            "message": "Ticket procesado correctamente",
            "ticket": TicketResponse.from_orm(ticket),
            "processing_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando ticket: {str(e)}")

@app.post("/tickets/process-pending/")
def process_all_pending_tickets(db: Session = Depends(get_db)):
    """Procesar todos los tickets pendientes"""
    try:
        # Obtener tickets pendientes
        pending_tickets = db.query(Ticket).filter(Ticket.status == "pending").all()
        
        if not pending_tickets:
            return {"message": "No hay tickets pendientes de procesamiento"}
        
        if not AI_AVAILABLE:
            return {
                "message": "AI system no disponible",
                "total_tickets": len(pending_tickets),
                "processed_count": 0,
                "failed_count": len(pending_tickets)
            }
        
        # Procesar cada ticket
        market_service = get_market_store_service(db)
        processed_count = 0
        failed_count = 0
        
        for ticket in pending_tickets:
            try:
                result = process_ticket_with_ai(ticket.file_path, market_service)
                
                # Verificar si es un ticket duplicado
                if result.get('procesado_correctamente', False):
                    is_duplicate = check_duplicate_ticket(result, ticket.user_id, db)
                    if is_duplicate:
                        # Marcar como duplicado
                        result['ticket_status'] = 'duplicate'
                        result['status_message'] = 'Ticket duplicado detectado'
                        result['duplicate_detected'] = True
                        print(f"   ⚠️ Ticket duplicado detectado para usuario {ticket.user_id}")
                
                # Actualizar ticket
                ticket.status = result.get('ticket_status', 'failed')
                ticket.processing_result = result
                ticket.updated_at = datetime.now()
                
                if result.get('ticket_status') in ['done_approved', 'done_rejected'] and not result.get('duplicate_detected', False):
                    processed_count += 1
                    update_purchase_history(ticket, result) # Actualizar historial para tickets aprobados/rechazados
                elif result.get('ticket_status') == 'duplicate':
                    processed_count += 1  # Contar como procesado pero no actualizar historial
                else:
                    failed_count += 1
                
                # Actualizar gamificación para todos los tickets procesados (excepto duplicados)
                if not result.get('duplicate_detected', False):
                    update_gamification(ticket, result)
                    
            except Exception as e:
                ticket.status = "failed"
                ticket.processing_result = {"error": str(e)}
                ticket.updated_at = datetime.now()
                failed_count += 1
        
        db.commit()
        
        return {
            "message": f"Procesamiento completado",
            "total_tickets": len(pending_tickets),
            "processed_count": processed_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando tickets: {str(e)}")

@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: uuid.UUID, db: Session = Depends(get_db)):
    """Obtener información detallada de un ticket específico"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket

@app.get("/tickets/history/{user_id}")
@app.get("/history/{user_id}")
def get_user_ticket_history(
    user_id: str,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener historial completo de tickets de un usuario con todos los estados"""
    try:
        print(f"🔍 Buscant historial per usuari: {user_id}")
        
        # Validar UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID d'usuari invàlid")
        
        query = db.query(Ticket).filter(Ticket.user_id == user_uuid)
        
        if status:
            query = query.filter(Ticket.status == status)
        
        tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
        print(f"📊 Trobats {len(tickets)} tickets per l'usuari {user_id}")
        
        response_tickets = []
        for ticket in tickets:
            base = TicketResponse.from_orm(ticket).dict()
            if base.get('ticket_metadata', {}).get('type') == 'digital':
                store_name = base['ticket_metadata'].get('store_name', 'Tienda Digital')
                base['display_name'] = f"Ticket Digital - {store_name}"
                base['store_name'] = store_name
                base['total_amount'] = base['ticket_metadata'].get('total_amount', 0.0)
                base['products'] = base['ticket_metadata'].get('products', [])
                base['is_digital'] = True
            else:
                processing = base.get('processing_result', {}) or {}
                store_name = processing.get('tienda', 'Desconocida')
                base['display_name'] = f"Compra - {store_name}"
                base['store_name'] = store_name
                base['total_amount'] = processing.get('total', 0.0)
                base['products'] = processing.get('productos', [])
                base['is_digital'] = False
            response_tickets.append(base)
        
        print(f"✅ Retornant {len(response_tickets)} tickets processats")
        return response_tickets
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error obtenint historial: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obtenint historial: {str(e)}")

@app.get("/tickets/digital/{user_id}")
def get_user_digital_tickets(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener solo tickets digitales de un usuario"""
    try:
        tickets = db.query(Ticket).filter(
            Ticket.user_id == uuid.UUID(user_id),
            Ticket.ticket_metadata.contains({"type": "digital"})
        ).order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()

        response_tickets = []
        for ticket in tickets:
            base = TicketResponse.from_orm(ticket).dict()
            store_name = base.get('ticket_metadata', {}).get('store_name', 'Tienda Digital')
            base['display_name'] = f"Ticket Digital - {store_name}"
            base['store_name'] = store_name
            base['total_amount'] = base.get('ticket_metadata', {}).get('total_amount', 0.0)
            base['products'] = base.get('ticket_metadata', {}).get('products', [])
            base['is_digital'] = True
            response_tickets.append(base)

        return response_tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tickets digitales: {str(e)}")

@app.get("/debug/user-info")
def debug_user_info():
    """Endpoint de debug per verificar l'estat de l'usuari"""
    return {
        "message": "Ticket service funciona correctament",
        "timestamp": datetime.now().isoformat(),
        "available_users": [
            {
                "id": "afdd45db-0aac-4b26-af5f-ff9ad39ec7f2",
                "email": "pato@pato.pato",
                "tickets_count": 4
            },
            {
                "id": "7df6e3c1-062f-4ede-9ce4-c9e60a73ad9b", 
                "email": "admin@tfg.com",
                "tickets_count": 2
            }
        ],
        "endpoints": {
            "health": "/health",
            "ticket_history": "/tickets/history/{user_id}",
            "debug_user_info": "/debug/user-info"
        }
    }

@app.get("/health")
def health_check():
    """Verificar estado del servicio"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "duplicate_detection_enabled": settings.ENABLE_DUPLICATE_DETECTION,
        "service": "ticket-service",
        "version": "1.0.0"
    } 