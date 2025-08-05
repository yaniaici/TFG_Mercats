#!/usr/bin/env python3
"""
Script para probar el procesamiento de tickets con el servicio Docker
"""

import requests
import json
import os

def test_ticket_processing():
    """Probar el procesamiento de ticket.jpg"""
    
    # Verificar que el archivo existe
    ticket_path = "images/ticket.jpg"
    if not os.path.exists(ticket_path):
        print(f"❌ Error: No se encuentra el archivo {ticket_path}")
        return
    
    print("🎫 TESTING TICKET PROCESSING")
    print("=" * 50)
    print(f"📁 Archivo: {ticket_path}")
    print(f"📏 Tamaño: {os.path.getsize(ticket_path)} bytes")
    
    # Preparar la petición
    url = "http://localhost:8003/process-ticket"
    
    try:
        # Abrir el archivo y enviar la petición
        with open(ticket_path, 'rb') as f:
            files = {'file': ('ticket.jpg', f, 'image/jpeg')}
            
            print("\n🚀 Enviando imagen al servicio...")
            response = requests.post(url, files=files)
        
        # Procesar la respuesta
        if response.status_code == 200:
            result = response.json()
            print("✅ Ticket procesado exitosamente!")
            print("\n📋 RESULTADOS:")
            print(f"   📅 Fecha: {result.get('fecha', 'No detectada')}")
            print(f"   🕐 Hora: {result.get('hora', 'No detectada')}")
            print(f"   🏪 Tienda: {result.get('tienda', 'No detectada')}")
            print(f"   💰 Total: {result.get('total', 'No detectado')} €")
            print(f"   🏷️ Tipo: {result.get('tipo_ticket', 'No detectado')}")
            print(f"   📦 Productos: {result.get('num_productos', 0)}")
            print(f"   ✅ Procesado: {'Sí' if result.get('procesado_correctamente') else 'No'}")
            print(f"   🤖 Método: {result.get('metodo', 'No especificado')}")
            
            # Mostrar error si existe
            if result.get('error'):
                print(f"   ❌ Error: {result.get('error')}")
            
            # Mostrar productos si hay
            if result.get('productos'):
                print(f"\n🛒 PRODUCTOS DETECTADOS ({len(result['productos'])}):")
                for i, producto in enumerate(result['productos'], 1):
                    print(f"   {i}. {producto['cantidad']}x {producto['nombre']} - {producto['precio']} €")
            
            # Mostrar respuesta de Gemini (primeros 200 caracteres)
            raw_response = result.get('raw_gemini_response', '')
            if raw_response:
                print(f"\n🤖 RESPUESTA GEMINI (primeros 200 chars):")
                print(f"   {raw_response[:200]}...")
            
            # Mostrar respuesta completa si hay error
            if not result.get('procesado_correctamente'):
                print(f"\n🔍 RESPUESTA COMPLETA:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ Error en el procesamiento: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servicio en localhost:8003")
        print("   Asegúrate de que el Docker esté ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_ticket_processing() 