import requests

# URLs
AUTH_URL = "http://localhost:8001"
TICKET_URL = "http://localhost:8003"

print("🔐 Creando usuario y probando autenticación...")

# 1. Registrar usuario
print("\n1. Registrando usuario...")
register_data = {
    "email_hash": "nuevo@test.com",
    "password": "password123"
}

try:
    response = requests.post(f"{AUTH_URL}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [201, 400]:  # 201 = creado, 400 = ya existe
        print("✅ Usuario registrado o ya existe")
        
        # 2. Login
        print("\n2. Haciendo login...")
        login_data = {
            "email_hash": "nuevo@test.com",
            "password": "password123"
        }
        
        login_response = requests.post(f"{AUTH_URL}/auth/login", json=login_data)
        print(f"Status: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("access_token")
            print(f"Token obtenido: {token[:30]}...")
            
            # 3. Verificar token en auth-service
            print("\n3. Verificando token en auth-service...")
            verify_response = requests.post(f"{AUTH_URL}/auth/verify", data={"token": token})
            print(f"Status: {verify_response.status_code}")
            print(f"Response: {verify_response.text}")
            
            # 4. Probar ticket-service
            print("\n4. Probando ticket-service...")
            headers = {"Authorization": f"Bearer {token}"}
            ticket_response = requests.get(f"{TICKET_URL}/tickets", headers=headers)
            print(f"Status: {ticket_response.status_code}")
            print(f"Response: {ticket_response.text}")
            
        else:
            print("❌ Login falló")
    else:
        print("❌ Registro falló")
        
except Exception as e:
    print(f"❌ Error: {e}") 