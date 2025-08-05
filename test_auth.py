import requests
import json

# URLs de los servicios
AUTH_URL = "http://localhost:8001"
TICKET_URL = "http://localhost:8003"

def test_auth_flow():
    print("🔐 Probando flujo de autenticación...")
    
    # 1. Registrar usuario
    print("\n1. Registrando usuario...")
    register_data = {
        "email_hash": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/auth/register", json=register_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ Usuario registrado exitosamente")
        elif response.status_code == 400 and "already exists" in response.text:
            print("   ℹ️ Usuario ya existe, continuando...")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return
    
    # 2. Login para obtener token
    print("\n2. Haciendo login...")
    login_data = {
        "email_hash": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            token = login_response.get("access_token")
            user_id = login_response.get("user_id")
            print(f"   ✅ Login exitoso")
            print(f"   Token: {token[:20]}...")
            print(f"   User ID: {user_id}")
        else:
            print(f"   ❌ Error: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return
    
    # 3. Verificar token directamente en auth-service
    print("\n3. Verificando token en auth-service...")
    try:
        response = requests.post(f"{AUTH_URL}/auth/verify", data={"token": token})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            verify_response = response.json()
            print(f"   ✅ Token válido: {verify_response}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 4. Probar endpoint protegido en ticket-service
    print("\n4. Probando endpoint protegido en ticket-service...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{TICKET_URL}/tickets", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Autenticación exitosa en ticket-service")
            tickets = response.json()
            print(f"   Tickets encontrados: {len(tickets)}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_auth_flow() 