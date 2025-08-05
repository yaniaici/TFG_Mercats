#!/usr/bin/env python3
"""
Script para probar la integración entre auth-service y main-backend
"""

import requests
import json
import time
from datetime import datetime

# Configuración
AUTH_SERVICE_URL = "http://localhost:8001"
MAIN_BACKEND_URL = "http://localhost:8000"

def test_auth_service():
    """Probar el servicio de autenticación"""
    print("🔐 Probando Auth Service...")
    
    # 1. Registrar usuario
    print("  1. Registrando usuario...")
    register_data = {
        "email_hash": "test@example.com",
        "password": "test123",
        "preferences": {"theme": "dark"}
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            user = response.json()
            print(f"     ✅ Usuario registrado: {user['id']}")
        else:
            print(f"     ❌ Error al registrar: {response.status_code}")
            print(f"     {response.text}")
            return None
    except Exception as e:
        print(f"     ❌ Error de conexión: {e}")
        return None
    
    # 2. Login
    print("  2. Haciendo login...")
    login_data = {
        "email_hash": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["access_token"]
            user_id = login_result["user_id"]
            print(f"     ✅ Login exitoso: {user_id}")
            return token, user_id
        else:
            print(f"     ❌ Error en login: {response.status_code}")
            print(f"     {response.text}")
            return None
    except Exception as e:
        print(f"     ❌ Error de conexión: {e}")
        return None

def test_main_backend(token):
    """Probar el backend principal con el token"""
    print("\n🚀 Probando Main Backend...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Crear perfil de usuario
    print("  1. Creando perfil de usuario...")
    profile_data = {
        "user_type": "regular",
        "segment": "test_segment"
    }
    
    try:
        response = requests.post(
            f"{MAIN_BACKEND_URL}/users/{user_id}/profile", 
            json=profile_data,
            headers=headers
        )
        if response.status_code == 201:
            profile = response.json()
            print(f"     ✅ Perfil creado: {profile['id']}")
        else:
            print(f"     ❌ Error al crear perfil: {response.status_code}")
            print(f"     {response.text}")
    except Exception as e:
        print(f"     ❌ Error de conexión: {e}")
    
    # 2. Crear ticket
    print("  2. Creando ticket...")
    ticket_data = {
        "purchase_datetime": datetime.now().isoformat(),
        "store_id": "test_store_123",
        "total_price": 25.50,
        "origin": "digital",
        "ticket_hash": "hash_test_123"
    }
    
    try:
        response = requests.post(
            f"{MAIN_BACKEND_URL}/tickets",
            json=ticket_data,
            headers=headers
        )
        if response.status_code == 201:
            ticket = response.json()
            print(f"     ✅ Ticket creado: {ticket['id']}")
        else:
            print(f"     ❌ Error al crear ticket: {response.status_code}")
            print(f"     {response.text}")
    except Exception as e:
        print(f"     ❌ Error de conexión: {e}")
    
    # 3. Obtener estadísticas
    print("  3. Obteniendo estadísticas...")
    try:
        response = requests.get(f"{MAIN_BACKEND_URL}/analytics/user-stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"     ✅ Estadísticas obtenidas:")
            print(f"       - Tickets totales: {stats['total_tickets']}")
            print(f"       - Gasto total: {stats['total_spent']}")
            print(f"       - Puntos: {stats['gamification_points']}")
        else:
            print(f"     ❌ Error al obtener estadísticas: {response.status_code}")
            print(f"     {response.text}")
    except Exception as e:
        print(f"     ❌ Error de conexión: {e}")

def test_health_checks():
    """Probar health checks de ambos servicios"""
    print("\n🏥 Probando Health Checks...")
    
    # Auth Service
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/health")
        if response.status_code == 200:
            print(f"   ✅ Auth Service: {response.json()}")
        else:
            print(f"   ❌ Auth Service: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Auth Service: {e}")
    
    # Main Backend
    try:
        response = requests.get(f"{MAIN_BACKEND_URL}/health")
        if response.status_code == 200:
            print(f"   ✅ Main Backend: {response.json()}")
        else:
            print(f"   ❌ Main Backend: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Main Backend: {e}")

def main():
    """Función principal"""
    print("🧪 Iniciando pruebas de integración...")
    print(f"   Auth Service: {AUTH_SERVICE_URL}")
    print(f"   Main Backend: {MAIN_BACKEND_URL}")
    
    # Probar health checks
    test_health_checks()
    
    # Probar auth service
    result = test_auth_service()
    if result is None:
        print("\n❌ No se pudo obtener token. Abortando pruebas.")
        return
    
    token, user_id = result
    
    # Probar main backend
    test_main_backend(token)
    
    print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    main() 