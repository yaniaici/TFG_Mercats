#!/usr/bin/env python3
"""
Script de prueba para el Ticket Service
"""

import requests
import json
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8003"
AUTH_URL = "http://localhost:8001"

def test_auth_service():
    """Probar que el auth-service esté funcionando"""
    print("🔍 Probando auth-service...")
    
    try:
        response = requests.get(f"{AUTH_URL}/health")
        if response.status_code == 200:
            print("✅ Auth-service está funcionando")
            return True
        else:
            print("❌ Auth-service no responde correctamente")
            return False
    except Exception as e:
        print(f"❌ Error conectando con auth-service: {e}")
        return False

def test_ticket_service_health():
    """Probar que el ticket-service esté funcionando"""
    print("🔍 Probando ticket-service...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Ticket-service está funcionando")
            return True
        else:
            print("❌ Ticket-service no responde correctamente")
            return False
    except Exception as e:
        print(f"❌ Error conectando con ticket-service: {e}")
        return False

def create_test_user():
    """Crear un usuario de prueba"""
    print("👤 Creando usuario de prueba...")
    
    user_data = {
        "email_hash": "test@example.com",
        "password": "testpassword123",
        "preferences": {"theme": "dark"}
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            print("✅ Usuario de prueba creado")
            return user_data
        elif response.status_code == 400 and "ya existe" in response.json().get("detail", ""):
            print("ℹ️ Usuario de prueba ya existe")
            return user_data
        else:
            print(f"❌ Error creando usuario: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return None

def login_user(user_data):
    """Iniciar sesión con el usuario de prueba"""
    print("🔐 Iniciando sesión...")
    
    login_data = {
        "email_hash": user_data["email_hash"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login exitoso")
            return token_data["access_token"]
        else:
            print(f"❌ Error en login: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def create_test_image():
    """Crear una imagen de prueba"""
    print("🖼️ Creando imagen de prueba...")
    
    # Crear una imagen simple de 100x100 píxeles
    from PIL import Image, ImageDraw
    
    img = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 40), "TEST TICKET", fill='black')
    
    # Guardar imagen
    test_image_path = "test_ticket.jpg"
    img.save(test_image_path, "JPEG")
    
    print(f"✅ Imagen de prueba creada: {test_image_path}")
    return test_image_path

def test_upload_ticket(token, image_path):
    """Probar subida de ticket"""
    print("📤 Probando subida de ticket...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/tickets/upload", headers=headers, files=files)
        
        if response.status_code == 201:
            ticket_data = response.json()
            print("✅ Ticket subido exitosamente")
            print(f"   ID: {ticket_data['ticket']['id']}")
            print(f"   Estado: {ticket_data['ticket']['status']}")
            return ticket_data['ticket']['id']
        else:
            print(f"❌ Error subiendo ticket: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en subida: {e}")
        return None

def test_get_tickets(token):
    """Probar obtención de tickets"""
    print("📋 Probando obtención de tickets...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/tickets", headers=headers)
        if response.status_code == 200:
            tickets = response.json()
            print(f"✅ Tickets obtenidos: {len(tickets)}")
            return tickets
        else:
            print(f"❌ Error obteniendo tickets: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo tickets: {e}")
        return None

def test_get_specific_ticket(token, ticket_id):
    """Probar obtención de ticket específico"""
    print(f"🔍 Probando obtención de ticket {ticket_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/tickets/{ticket_id}", headers=headers)
        if response.status_code == 200:
            ticket = response.json()
            print("✅ Ticket específico obtenido")
            print(f"   Nombre original: {ticket['original_filename']}")
            print(f"   Tamaño: {ticket['file_size']} bytes")
            return ticket
        else:
            print(f"❌ Error obteniendo ticket específico: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo ticket específico: {e}")
        return None

def test_update_ticket(token, ticket_id):
    """Probar actualización de ticket"""
    print(f"✏️ Probando actualización de ticket {ticket_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "status": "processed",
        "metadata": {"store": "Test Store", "amount": 25.50},
        "processing_result": {"total": 25.50, "items": 3}
    }
    
    try:
        response = requests.put(f"{BASE_URL}/tickets/{ticket_id}", headers=headers, json=update_data)
        if response.status_code == 200:
            ticket = response.json()
            print("✅ Ticket actualizado exitosamente")
            print(f"   Nuevo estado: {ticket['status']}")
            return ticket
        else:
            print(f"❌ Error actualizando ticket: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error actualizando ticket: {e}")
        return None

def test_delete_ticket(token, ticket_id):
    """Probar eliminación de ticket"""
    print(f"🗑️ Probando eliminación de ticket {ticket_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/tickets/{ticket_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Ticket eliminado exitosamente")
            return True
        else:
            print(f"❌ Error eliminando ticket: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error eliminando ticket: {e}")
        return False

def cleanup_test_files(image_path):
    """Limpiar archivos de prueba"""
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"🧹 Archivo de prueba eliminado: {image_path}")
    except Exception as e:
        print(f"⚠️ Error eliminando archivo de prueba: {e}")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del Ticket Service")
    print("=" * 50)
    
    # Verificar servicios
    if not test_auth_service():
        print("❌ Auth-service no disponible. Abortando pruebas.")
        return
    
    if not test_ticket_service_health():
        print("❌ Ticket-service no disponible. Abortando pruebas.")
        return
    
    # Crear usuario y obtener token
    user_data = create_test_user()
    if not user_data:
        print("❌ No se pudo crear/obtener usuario. Abortando pruebas.")
        return
    
    token = login_user(user_data)
    if not token:
        print("❌ No se pudo obtener token. Abortando pruebas.")
        return
    
    # Crear imagen de prueba
    image_path = create_test_image()
    
    try:
        # Probar subida de ticket
        ticket_id = test_upload_ticket(token, image_path)
        if not ticket_id:
            print("❌ No se pudo subir ticket. Abortando pruebas.")
            return
        
        # Probar obtención de tickets
        tickets = test_get_tickets(token)
        if not tickets:
            print("❌ No se pudieron obtener tickets.")
        
        # Probar obtención de ticket específico
        ticket = test_get_specific_ticket(token, ticket_id)
        if not ticket:
            print("❌ No se pudo obtener ticket específico.")
        
        # Probar actualización de ticket
        updated_ticket = test_update_ticket(token, ticket_id)
        if not updated_ticket:
            print("❌ No se pudo actualizar ticket.")
        
        # Probar eliminación de ticket
        if not test_delete_ticket(token, ticket_id):
            print("❌ No se pudo eliminar ticket.")
        
        print("\n" + "=" * 50)
        print("✅ Todas las pruebas completadas exitosamente!")
        
    finally:
        # Limpiar archivos de prueba
        cleanup_test_files(image_path)

if __name__ == "__main__":
    main() 