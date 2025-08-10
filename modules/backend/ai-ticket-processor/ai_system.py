import requests
import json
import os
import base64
from datetime import datetime
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()

class GeminiTicketAI:
    def __init__(self, market_store_service=None):
        """
        Sistema de IA para procesamiento de tickets usando Gemini API
        """
        print("🚀 Inicializando Sistema de IA con Gemini...")
        
        # Obtener API key de Gemini
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        # Servicio para verificar tiendas del mercado
        self.market_store_service = market_store_service
        
        print("✅ Sistema de IA con Gemini inicializado correctamente")

    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Codificar imagen a base64 para enviar a Gemini
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error("Error encoding image to base64", error=str(e), image_path=image_path)
            raise

    def call_gemini_api(self, image_base64: str) -> str:
        """
        Llamar a la API de Gemini con la imagen
        """
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
        # Prompt específico para procesar tickets
        prompt = """
        Analiza esta imagen de un ticket de compra y extrae la siguiente información en formato JSON:

        {
            "fecha": "fecha del ticket (formato DD/MM/YYYY o similar)",
            "hora": "hora del ticket (formato HH:MM)",
            "tienda": "nombre de la tienda o establecimiento",
            "total": "importe total del ticket (solo el número)",
            "tipo_ticket": "tipo de ticket (supermercado, restaurante, gasolinera, farmacia, otros)",
            "productos": [
                {
                    "cantidad": "cantidad del producto",
                    "nombre": "nombre del producto",
                    "precio": "precio del producto (solo el número)"
                }
            ]
        }

        Reglas importantes:
        - Si no encuentras algún campo, ponlo como null
        - Para productos, extrae solo los que sean claramente productos (no totales, impuestos, etc.)
        - Los precios deben ser solo números (sin símbolos de moneda)
        - La fecha debe estar en formato DD/MM/YYYY si es posible
        - La hora debe estar en formato HH:MM
        - El tipo de ticket debe ser uno de: supermercado, restaurante, gasolinera, farmacia, otros
        - Responde SOLO con el JSON, sin texto adicional
        """
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            print("🌐 Enviando petición a Gemini API...")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"📡 Respuesta de Gemini API: Status {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Respuesta exitosa de Gemini API")
                
                # Extraer el texto de la respuesta
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        response_text = content['parts'][0]['text']
                        print(f"📝 Texto extraído de Gemini: {len(response_text)} caracteres")
                        print(f"🔍 Primeros 300 caracteres: {response_text[:300]}...")
                        return response_text
                
                print("❌ Respuesta de Gemini no tiene el formato esperado")
                raise ValueError("Respuesta de Gemini no tiene el formato esperado")
            else:
                print(f"❌ Error en API de Gemini: {response.status_code}")
                print(f"📄 Respuesta de error: {response.text}")
                logger.error("Error en API de Gemini", status_code=response.status_code, response=response.text)
                raise ValueError(f"Error en API de Gemini: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 Error de conexión con Gemini API: {str(e)}")
            logger.error("Error de conexión con Gemini API", error=str(e))
            raise

    def parse_gemini_response(self, response_text: str) -> Dict:
        """
        Parsear la respuesta de Gemini y extraer el JSON
        """
        try:
            print("🔍 Iniciando parseo de respuesta de Gemini...")
            
            # Limpiar la respuesta para extraer solo el JSON
            response_text = response_text.strip()
            print(f"📝 Respuesta limpia: {len(response_text)} caracteres")
            
            # Buscar el JSON en la respuesta
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            print(f"🔍 Buscando JSON: inicio en {start_idx}, fin en {end_idx}")
            
            if start_idx == -1 or end_idx == 0:
                print("❌ No se encontró JSON válido en la respuesta")
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            json_str = response_text[start_idx:end_idx]
            print(f"📋 JSON extraído: {len(json_str)} caracteres")
            print(f"🔍 JSON: {json_str}")
            
            parsed_data = json.loads(json_str)
            print("✅ JSON parseado correctamente")
            
            # Validar estructura básica
            required_fields = ['fecha', 'hora', 'tienda', 'total', 'tipo_ticket', 'productos']
            print("🔍 Validando campos requeridos...")
            for field in required_fields:
                if field not in parsed_data:
                    print(f"   ⚠️ Campo '{field}' no encontrado, estableciendo como None")
                    parsed_data[field] = None
                else:
                    print(f"   ✅ Campo '{field}': {parsed_data[field]}")
            
            # Asegurar que productos sea una lista
            if not isinstance(parsed_data.get('productos'), list):
                print("⚠️ Campo 'productos' no es una lista, estableciendo como lista vacía")
                parsed_data['productos'] = []
            else:
                print(f"✅ Campo 'productos': {len(parsed_data['productos'])} items")
            
            print("✅ Parseo completado exitosamente")
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {str(e)}")
            logger.error("Error parseando JSON de Gemini", error=str(e), response=response_text)
            raise ValueError(f"Error parseando JSON: {str(e)}")
        except Exception as e:
            print(f"❌ Error procesando respuesta: {str(e)}")
            logger.error("Error procesando respuesta de Gemini", error=str(e))
            raise

    def verify_market_store(self, store_name: str) -> bool:
        """
        Verificar si una tienda es del mercado
        """
        print(f"🔍 Verificando tienda: '{store_name}'")
        
        if not store_name:
            print("   ⚠️ Nombre de tienda vacío")
            return False
        
        # Obtener tiendas del mercado desde el ticket service
        try:
            import requests
            response = requests.get("http://ticket-service:8003/market-stores/", timeout=10)
            if response.status_code == 200:
                market_stores = response.json()
                market_store_names = [store.get('name', '') for store in market_stores if store.get('is_active', True)]
                
                print(f"   📋 Tiendas del mercado disponibles: {market_store_names}")
                
                # Verificar si el nombre de la tienda contiene alguna de las tiendas del mercado
                store_name_lower = store_name.lower()
                for market_store in market_store_names:
                    if market_store.lower() in store_name_lower:
                        print(f"   ✅ Coincidencia encontrada: '{market_store}' en '{store_name}'")
                        return True
                
                print(f"   ❌ No es tienda del mercado")
                return False
            else:
                print(f"   ⚠️ Error obteniendo tiendas del mercado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ⚠️ Error verificando tienda del mercado: {str(e)}")
            return False

    def process_ticket(self, image_path: str) -> Dict:
        """
        Procesar ticket completo usando Gemini API
        """
        print(f"🎫 Procesando ticket con Gemini: {image_path}")
        logger.info("Iniciando procesamiento de ticket", image_path=image_path)
        
        try:
            # Codificar imagen a base64
            print("📸 Codificando imagen a base64...")
            image_base64 = self.encode_image_to_base64(image_path)
            print(f"✅ Imagen codificada: {len(image_base64)} caracteres base64")
            
            # Llamar a Gemini API
            print("🤖 Enviando imagen a Gemini API...")
            gemini_response = self.call_gemini_api(image_base64)
            print(f"✅ Respuesta de Gemini recibida: {len(gemini_response)} caracteres")
            
            # Parsear respuesta
            print("🔍 Parseando respuesta de Gemini...")
            parsed_data = self.parse_gemini_response(gemini_response)
            
            # Logs detallados de cada elemento extraído
            print("\n📋 ELEMENTOS EXTRAÍDOS DEL TICKET:")
            print(f"   📅 Fecha: {parsed_data.get('fecha', 'No detectada')}")
            print(f"   🕐 Hora: {parsed_data.get('hora', 'No detectada')}")
            print(f"   🏪 Tienda: {parsed_data.get('tienda', 'No detectada')}")
            print(f"   💰 Total: {parsed_data.get('total', 'No detectado')} €")
            print(f"   🏷️ Tipo: {parsed_data.get('tipo_ticket', 'No detectado')}")
            print(f"   📦 Productos: {len(parsed_data.get('productos', []))} items")
            
            # Mostrar productos si hay
            productos = parsed_data.get('productos', [])
            if productos:
                print(f"\n🛒 PRODUCTOS DETECTADOS ({len(productos)}):")
                for i, producto in enumerate(productos, 1):
                    print(f"   {i}. {producto.get('cantidad', '?')}x {producto.get('nombre', 'Producto desconocido')} - {producto.get('precio', '?')} €")
            
            # Verificar si es tienda del mercado
            store_name = parsed_data.get('tienda')
            print(f"\n🏪 VERIFICANDO TIENDA DEL MERCADO:")
            print(f"   Nombre de tienda: {store_name}")
            
            es_tienda_mercado = self.verify_market_store(store_name) if store_name else False
            print(f"   ¿Es tienda del mercado? {'✅ SÍ' if es_tienda_mercado else '❌ NO'}")
            
            # Determinar el estado del ticket
            if parsed_data.get('procesado_correctamente', True):
                if es_tienda_mercado:
                    ticket_status = "done_approved"
                    status_message = "Ticket aprobado - Tienda del mercado"
                    print(f"   🎉 RESULTADO: TICKET APROBADO")
                else:
                    ticket_status = "done_rejected"
                    status_message = "Ticket rechazado - No es tienda del mercado"
                    print(f"   ⚠️ RESULTADO: TICKET RECHAZADO (no es tienda del mercado)")
            else:
                ticket_status = "failed"
                status_message = "Error en el procesamiento"
                print(f"   💥 RESULTADO: TICKET FALLIDO (error en procesamiento)")
            
            # Estructurar resultado final
            result = {
                'fecha': parsed_data.get('fecha'),
                'hora': parsed_data.get('hora'),
                'tienda': parsed_data.get('tienda'),
                'total': parsed_data.get('total'),
                'tipo_ticket': parsed_data.get('tipo_ticket', 'otros'),
                'productos': parsed_data.get('productos', []),
                'num_productos': len(parsed_data.get('productos', [])),
                'texto_extraido': f"Procesado con Gemini API - {len(gemini_response)} caracteres",
                'procesado_correctamente': True,
                'es_tienda_mercado': es_tienda_mercado,
                'ticket_status': ticket_status,
                'status_message': status_message,
                'metodo': 'Gemini 2.0 Flash API',
                'timestamp': datetime.now().isoformat(),
                'raw_gemini_response': gemini_response[:200] + "..." if len(gemini_response) > 200 else gemini_response
            }
            
            print(f"\n✅ Ticket procesado con Gemini: {result['tienda']} - {result['num_productos']} productos - Estado: {ticket_status}")
            logger.info("Ticket procesado exitosamente", 
                       tienda=result['tienda'], 
                       productos=result['num_productos'], 
                       estado=ticket_status,
                       es_tienda_mercado=es_tienda_mercado)
            return result
            
        except Exception as e:
            logger.error("Error procesando ticket con Gemini", error=str(e), image_path=image_path)
            return {
                'fecha': None,
                'hora': None,
                'tienda': None,
                'total': None,
                'tipo_ticket': 'desconocido',
                'productos': [],
                'num_productos': 0,
                'texto_extraido': '',
                'procesado_correctamente': False,
                'es_tienda_mercado': False,
                'ticket_status': 'failed',
                'status_message': f'Error en el procesamiento: {str(e)}',
                'error': str(e),
                'metodo': 'Gemini 2.0 Flash API (error)',
                'timestamp': datetime.now().isoformat()
            }

# Alias para compatibilidad
FinalTicketAI = GeminiTicketAI 