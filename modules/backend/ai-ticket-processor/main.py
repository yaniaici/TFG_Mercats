
import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import structlog
import tempfile
import shutil

# Importar el sistema de IA
from ai_system import GeminiTicketAI

# Importar procesador automático
from auto_processor import get_auto_processor

# Cargar variables de entorno
load_dotenv()

# Configurar logging estructurado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Crear aplicación FastAPI
app = FastAPI(
    title="AI Ticket Processor API",
    description="Servicio de procesamiento de tickets con IA local",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el procesador de IA
ai_processor = None

@app.on_event("startup")
async def startup_event():
    """Inicializar el procesador de IA al arrancar la aplicación"""
    global ai_processor
    try:
        ai_processor = GeminiTicketAI()
        logger.info("AI processor initialized successfully")
        
        # Iniciar procesador automático
        auto_processor = get_auto_processor()
        auto_processor.start_processor()
        logger.info("Auto processor started")
        
    except Exception as e:
        logger.error("Failed to initialize AI processor", error=str(e))
        raise

@app.get("/")
async def root():
    """Endpoint de salud"""
    return {
        "service": "AI Ticket Processor API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {
        "status": "healthy",
        "ai_processor_ready": ai_processor is not None
    }

@app.post("/process-ticket-api")
async def process_ticket_api(request: Request):
    """
    Procesar ticket desde base64 y verificar tiendas del mercado
    
    Args:
        request: JSON con image_base64 y market_stores
        
    Returns:
        JSON con la información procesada del ticket
    """
    if ai_processor is None:
        raise HTTPException(status_code=503, detail="AI processor not initialized")
    
    try:
        # Obtener datos del request
        data = await request.json()
        image_base64 = data.get("image_base64")
        market_stores = data.get("market_stores", [])
        
        if not image_base64:
            raise HTTPException(status_code=400, detail="image_base64 is required")
        
        # Decodificar imagen base64
        import base64
        import tempfile
        
        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
        
        # Guardar imagen temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name
        
        try:
            # Procesar con IA
            result = ai_processor.process_ticket(temp_path)
            
            # Verificar si es tienda del mercado
            tienda = result.get('tienda', '')
            es_tienda_mercado = any(store.lower() in tienda.lower() for store in market_stores) if tienda else False
            
            # Determinar estado del ticket
            if result.get('procesado_correctamente', False):
                if es_tienda_mercado:
                    result['ticket_status'] = "done_approved"
                    result['status_message'] = "Ticket aprobado - Tienda del mercado"
                else:
                    result['ticket_status'] = "done_rejected"
                    result['status_message'] = "Ticket rechazado - No es tienda del mercado"
            else:
                result['ticket_status'] = "failed"
                result['status_message'] = "Error en el procesamiento"
            
            result['es_tienda_mercado'] = es_tienda_mercado
            
            return JSONResponse(content=result)
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error("Error processing ticket via API", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error processing ticket: {str(e)}")

@app.post("/process-ticket")
async def process_ticket(file: UploadFile = File(...)):
    """
    Procesar una imagen de ticket y extraer información
    
    Args:
        file: Archivo de imagen del ticket
        
    Returns:
        JSON con la información extraída del ticket
    """
    if ai_processor is None:
        raise HTTPException(status_code=503, detail="AI processor not initialized")
    
    # Validar tipo de archivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validar extensión
    allowed_extensions = {'.jpg', '.jpeg', '.png'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File extension {file_extension} not allowed. Use: {allowed_extensions}")
    
    temp_path = None
    try:
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Procesar con IA
        logger.info("Processing ticket", filename=file.filename)
        result = ai_processor.process_ticket(temp_path)
        
        logger.info("Ticket processed successfully", filename=file.filename)
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error("Error processing ticket", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail=f"Error processing ticket: {str(e)}")
    finally:
        # Limpiar archivo temporal al final
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning("Could not delete temporary file", error=str(e), temp_path=temp_path)

@app.post("/process-ticket-batch")
async def process_ticket_batch(files: list[UploadFile] = File(...)):
    """
    Procesar múltiples imágenes de tickets en lote
    
    Args:
        files: Lista de archivos de imagen de tickets
        
    Returns:
        Lista de resultados procesados
    """
    if ai_processor is None:
        raise HTTPException(status_code=503, detail="AI processor not initialized")
    
    results = []
    
    for file in files:
        try:
            # Validar tipo de archivo
            if not file.content_type.startswith('image/'):
                results.append({
                    "filename": file.filename,
                    "error": "File must be an image"
                })
                continue
            
            # Validar extensión
            allowed_extensions = {'.jpg', '.jpeg', '.png'}
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                results.append({
                    "filename": file.filename,
                    "error": f"File extension {file_extension} not allowed"
                })
                continue
            
            # Guardar archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_path = temp_file.name
            
            # Procesar con IA
            logger.info("Processing ticket in batch", filename=file.filename)
            result = ai_processor.process_ticket(temp_path)
            result["filename"] = file.filename
            results.append(result)
            
            # Limpiar archivo temporal
            os.unlink(temp_path)
            
        except Exception as e:
            logger.error("Error processing ticket in batch", error=str(e), filename=file.filename)
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return JSONResponse(content={"results": results})

@app.get("/model-info")
async def get_model_info():
    """Obtener información sobre el modelo de IA"""
    if ai_processor is None:
        raise HTTPException(status_code=503, detail="AI processor not initialized")
    
    return {
        "model_type": "Gemini 2.0 Flash API",
        "supported_languages": ["es", "en"],
        "supported_formats": ["jpg", "jpeg", "png"],
        "features": [
            "Date extraction",
            "Time extraction", 
            "Shop detection",
            "Product extraction",
            "Total amount extraction",
            "Ticket type classification",
            "AI-powered text recognition",
            "Structured JSON output"
        ]
    }

# Endpoints para el procesador automático
@app.get("/auto-processor/status")
async def get_auto_processor_status():
    """Obtener estado del procesador automático"""
    try:
        auto_processor = get_auto_processor()
        return auto_processor.get_status()
    except Exception as e:
        logger.error("Error getting auto processor status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/auto-processor/start")
async def start_auto_processor():
    """Iniciar el procesador automático"""
    try:
        auto_processor = get_auto_processor()
        auto_processor.start_processor()
        return {"message": "Auto processor started successfully"}
    except Exception as e:
        logger.error("Error starting auto processor", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/auto-processor/stop")
async def stop_auto_processor():
    """Detener el procesador automático"""
    try:
        auto_processor = get_auto_processor()
        auto_processor.stop_processor()
        return {"message": "Auto processor stopped successfully"}
    except Exception as e:
        logger.error("Error stopping auto processor", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/auto-processor/process-now")
async def process_now():
    """Procesar tickets pendientes inmediatamente"""
    try:
        auto_processor = get_auto_processor()
        result = auto_processor.process_pending_tickets()
        return result
    except Exception as e:
        logger.error("Error in manual processing", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
