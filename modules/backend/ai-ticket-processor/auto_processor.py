#!/usr/bin/env python3
"""
Módulo para procesamiento automático de tickets pendientes
"""

import time
import threading
import requests
import structlog
from datetime import datetime
from typing import Dict, List

logger = structlog.get_logger()

class AutoTicketProcessor:
    def __init__(self, ticket_service_url: str = "http://ticket-service:8003"):
        """
        Inicializar procesador automático de tickets
        
        Args:
            ticket_service_url: URL del servicio de tickets
        """
        self.ticket_service_url = ticket_service_url
        self.is_running = False
        self.thread = None
        self.processing_interval = 30  # segundos entre verificaciones
        
        print("🤖 Inicializando Auto Ticket Processor...")
        print(f"   📡 Ticket Service URL: {ticket_service_url}")
        print("   ⏰ Procesamiento continuo: verificar cada 30 segundos")
        print("   📋 Procesar tickets en orden de llegada (más antiguo primero)")
        
    def check_ticket_service_health(self) -> bool:
        """Verificar que el ticket service esté disponible"""
        try:
            response = requests.get(f"{self.ticket_service_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning("Ticket service no disponible", error=str(e))
            return False
    
    def get_pending_tickets(self) -> List[Dict]:
        """Obtener lista de tickets pendientes ordenados por fecha de creación"""
        try:
            response = requests.get(f"{self.ticket_service_url}/tickets/pending/", timeout=10)
            if response.status_code == 200:
                tickets = response.json()
                # Ordenar por fecha de creación (más antiguo primero)
                tickets.sort(key=lambda x: x.get('created_at', ''))
                return tickets
            return []
        except Exception as e:
            logger.error("Error obteniendo tickets pendientes", error=str(e))
            return []
    
    def get_pending_tickets_count(self) -> int:
        """Obtener cantidad de tickets pendientes"""
        tickets = self.get_pending_tickets()
        return len(tickets)
    
    def get_market_stores(self) -> List[str]:
        """Obtener lista de tiendas del mercado desde el ticket service"""
        try:
            response = requests.get(f"{self.ticket_service_url}/market-stores/", timeout=10)
            if response.status_code == 200:
                stores = response.json()
                return [store.get('name', '') for store in stores if store.get('is_active', True)]
            return []
        except Exception as e:
            logger.error("Error obteniendo tiendas del mercado", error=str(e))
            return []
    
    def is_market_store(self, store_name: str) -> bool:
        """Verificar si una tienda es del mercado"""
        if not store_name:
            return False
        
        market_stores = self.get_market_stores()
        if not market_stores:
            logger.warning("No se pudieron obtener las tiendas del mercado")
            return False
        
        # Verificar si el nombre de la tienda contiene alguna de las tiendas del mercado
        store_name_lower = store_name.lower()
        for market_store in market_stores:
            if market_store.lower() in store_name_lower:
                return True
        
        return False
    
    def check_duplicate_before_processing(self, ticket: Dict, ai_result: Dict) -> bool:
        """Verificar si el ticket es un duplicado antes de procesarlo"""
        try:
            # Extraer información del resultado de la IA
            fecha = ai_result.get('fecha', '')
            productos = ai_result.get('productos', [])
            user_id = ticket.get('user_id', '')
            
            if not fecha or not productos or not user_id:
                print(f"      ⚠️ Información insuficiente para verificar duplicados")
                return False
            
            # Llamar al endpoint de verificación de duplicados
            response = requests.post(
                f"{self.ticket_service_url}/check-duplicate",
                json={
                    "user_id": user_id,
                    "fecha": fecha,
                    "productos": productos
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('is_duplicate', False):
                    print(f"      ⚠️ Ticket duplicado detectado: {result.get('reason', '')}")
                    return True
                else:
                    print(f"      ✅ No es duplicado: {result.get('reason', '')}")
                    return False
            else:
                print(f"      ⚠️ Error verificando duplicados: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"      ⚠️ Error verificando duplicados: {str(e)}")
            return False

    def process_single_ticket(self, ticket: Dict) -> Dict:
        """Procesar un ticket individual"""
        ticket_id = ticket.get('id')
        filename = ticket.get('original_filename', 'Desconocido')
        
        print(f"   🎫 Procesando ticket: {filename} (ID: {ticket_id})")
        
        try:
            # Primero, procesar con IA para extraer información
            print(f"      🤖 Procesando con IA para extraer información...")
            
            # Obtener la imagen en base64 del ticket
            image_base64 = ticket.get('image_base64', '')
            print(f"      📁 Imagen en base64: {'Sí' if image_base64 else 'No'}")
            if not image_base64:
                print(f"      ❌ No se encontró la imagen en base64")
                return {"success": False, "ticket_id": ticket_id, "error": "No se encontró la imagen en base64"}
            
            print(f"      ✅ Imagen obtenida correctamente ({len(image_base64)} caracteres)")
            
            # Procesar con IA
            print(f"      🤖 Enviando a IA para procesamiento...")
            ai_response = requests.post(
                f"http://ai-ticket-processor:8004/process-ticket-api",
                json={
                    "image_base64": image_base64,
                    "market_stores": self.get_market_stores()
                },
                timeout=60
            )
            print(f"      📡 Respuesta de IA: {ai_response.status_code}")
            
            if ai_response.status_code != 200:
                error_msg = f"Error procesando con IA: {ai_response.status_code}"
                print(f"      ❌ {error_msg}")
                return {"success": False, "ticket_id": ticket_id, "error": error_msg}
            
            ai_result = ai_response.json()
            print(f"      ✅ IA procesó correctamente - Fecha: {ai_result.get('fecha', 'N/A')}, Productos: {len(ai_result.get('productos', []))}")
            
            # Verificar si es un duplicado antes de procesar
            if self.check_duplicate_before_processing(ticket, ai_result):
                # Si es duplicado, marcar el ticket como duplicado directamente
                print(f"      ⚠️ Ticket duplicado detectado, marcando como duplicado...")
                duplicate_response = requests.patch(
                    f"{self.ticket_service_url}/tickets/{ticket_id}/mark-duplicate",
                    json={
                        "processing_result": ai_result,
                        "status_message": "Ticket duplicado detectado"
                    },
                    timeout=30
                )
                
                if duplicate_response.status_code == 200:
                    print(f"      ✅ Ticket marcado como duplicado")
                    return {"success": True, "ticket_id": ticket_id, "result": {"ticket_status": "duplicate"}}
                else:
                    print(f"      ❌ Error marcando como duplicado: {duplicate_response.status_code}")
                    return {"success": False, "ticket_id": ticket_id, "error": "Error marcando como duplicado"}
            
            # Si no es duplicado, procesar normalmente
            print(f"      ✅ No es duplicado, procesando normalmente...")
            response = requests.post(
                f"{self.ticket_service_url}/tickets/{ticket_id}/process/",
                timeout=120  # 2 minutos de timeout por ticket
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ Procesado exitosamente")
                return {"success": True, "ticket_id": ticket_id, "result": result}
            else:
                error_msg = f"Error procesando ticket {ticket_id}: {response.status_code}"
                print(f"      ❌ {error_msg}")
                return {"success": False, "ticket_id": ticket_id, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error procesando ticket {ticket_id}: {str(e)}"
            print(f"      💥 {error_msg}")
            return {"success": False, "ticket_id": ticket_id, "error": error_msg}
    
    def process_pending_tickets(self) -> Dict:
        """Procesar tickets pendientes uno por uno en orden de llegada"""
        print(f"\n🔄 PROCESAMIENTO AUTOMÁTICO - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Verificar salud del servicio
            if not self.check_ticket_service_health():
                print("   ⚠️ Ticket service no disponible, saltando procesamiento")
                return {"error": "Ticket service no disponible"}
            
            # Obtener tickets pendientes ordenados
            pending_tickets = self.get_pending_tickets()
            print(f"   📋 Tickets pendientes encontrados: {len(pending_tickets)}")
            
            if not pending_tickets:
                print("   ✅ No hay tickets pendientes")
                return {"message": "No hay tickets pendientes"}
            
            # Procesar tickets uno por uno
            processed_count = 0
            failed_count = 0
            results = []
            
            for ticket in pending_tickets:
                result = self.process_single_ticket(ticket)
                results.append(result)
                
                if result.get('success'):
                    processed_count += 1
                else:
                    failed_count += 1
                
                # Pequeña pausa entre tickets para no sobrecargar
                time.sleep(2)
            
            print(f"   📊 RESUMEN:")
            print(f"      Total procesados: {processed_count}")
            print(f"      Fallidos: {failed_count}")
            
            logger.info("Procesamiento automático completado", 
                       total=len(pending_tickets),
                       processed=processed_count,
                       failed=failed_count)
            
            return {
                "total_tickets": len(pending_tickets),
                "processed_count": processed_count,
                "failed_count": failed_count,
                "results": results
            }
                
        except Exception as e:
            error_msg = f"Error en procesamiento automático: {str(e)}"
            print(f"   💥 {error_msg}")
            logger.error("Error en procesamiento automático", error=str(e))
            return {"error": error_msg}
    
    def start_processor(self):
        """Iniciar el procesador automático continuo"""
        if self.is_running:
            print("⚠️ Procesador ya está ejecutándose")
            return
        
        print("🚀 Iniciando procesador automático continuo...")
        
        # Procesar inmediatamente al iniciar
        print("🔄 Procesamiento inicial...")
        self.process_pending_tickets()
        
        self.is_running = True
        
        # Ejecutar procesador en un hilo separado
        def run_processor():
            while self.is_running:
                try:
                    # Verificar si hay tickets pendientes
                    pending_tickets = self.get_pending_tickets()
                    if pending_tickets:
                        print(f"🔄 Encontrados {len(pending_tickets)} tickets pendientes, procesando...")
                        self.process_pending_tickets()
                    else:
                        print("⏳ No hay tickets pendientes, esperando...")
                    
                    # Esperar antes de la siguiente verificación
                    time.sleep(self.processing_interval)
                    
                except Exception as e:
                    print(f"💥 Error en procesador automático: {str(e)}")
                    logger.error("Error en procesador automático", error=str(e))
                    time.sleep(self.processing_interval)
        
        self.thread = threading.Thread(target=run_processor, daemon=True)
        self.thread.start()
        
        print("✅ Procesador automático iniciado correctamente")
        logger.info("Auto processor iniciado")
    
    def stop_processor(self):
        """Detener el procesador automático"""
        if not self.is_running:
            return
        
        print("🛑 Deteniendo procesador automático...")
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=5)
        
        print("✅ Procesador automático detenido")
        logger.info("Auto processor detenido")
    
    def get_status(self) -> Dict:
        """Obtener estado del procesador automático"""
        return {
            "is_running": self.is_running,
            "ticket_service_url": self.ticket_service_url,
            "last_check": datetime.now().isoformat(),
            "pending_tickets": self.get_pending_tickets_count() if self.check_ticket_service_health() else "N/A"
        }

# Instancia global
auto_processor = None

def get_auto_processor() -> AutoTicketProcessor:
    """Obtener instancia del procesador automático"""
    global auto_processor
    if auto_processor is None:
        auto_processor = AutoTicketProcessor()
    return auto_processor 