import requests
import json
import os
import base64
from datetime import datetime
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()

class GeminiTicketAI:
    def __init__(self):
        """
        Sistema de IA para procesamiento de tickets usando Gemini API
        """
        print("🚀 Inicializando Sistema de IA con Gemini...")
        
        # Obtener API key de Gemini
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
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
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extraer el texto de la respuesta
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        return content['parts'][0]['text']
                
                raise ValueError("Respuesta de Gemini no tiene el formato esperado")
            else:
                logger.error("Error en API de Gemini", status_code=response.status_code, response=response.text)
                raise ValueError(f"Error en API de Gemini: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error("Error de conexión con Gemini API", error=str(e))
            raise

    def parse_gemini_response(self, response_text: str) -> Dict:
        """
        Parsear la respuesta de Gemini y extraer el JSON
        """
        try:
            # Limpiar la respuesta para extraer solo el JSON
            response_text = response_text.strip()
            
            # Buscar el JSON en la respuesta
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            json_str = response_text[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Validar estructura básica
            required_fields = ['fecha', 'hora', 'tienda', 'total', 'tipo_ticket', 'productos']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = None
            
            # Asegurar que productos sea una lista
            if not isinstance(parsed_data.get('productos'), list):
                parsed_data['productos'] = []
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error("Error parseando JSON de Gemini", error=str(e), response=response_text)
            raise ValueError(f"Error parseando JSON: {str(e)}")
        except Exception as e:
            logger.error("Error procesando respuesta de Gemini", error=str(e))
            raise

    def process_ticket(self, image_path: str) -> Dict:
        """
        Procesar ticket completo usando Gemini API
        """
        print(f"🎫 Procesando ticket con Gemini: {image_path}")
        
        try:
            # Codificar imagen a base64
            image_base64 = self.encode_image_to_base64(image_path)
            
            # Llamar a Gemini API
            gemini_response = self.call_gemini_api(image_base64)
            
            # Parsear respuesta
            parsed_data = self.parse_gemini_response(gemini_response)
            
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
                'metodo': 'Gemini 2.0 Flash API',
                'timestamp': datetime.now().isoformat(),
                'raw_gemini_response': gemini_response[:200] + "..." if len(gemini_response) > 200 else gemini_response
            }
            
            print(f"✅ Ticket procesado con Gemini: {result['tienda']} - {result['num_productos']} productos")
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
                'error': str(e),
                'metodo': 'Gemini 2.0 Flash API (error)',
                'timestamp': datetime.now().isoformat()
            }

# Alias para compatibilidad
FinalTicketAI = GeminiTicketAI 