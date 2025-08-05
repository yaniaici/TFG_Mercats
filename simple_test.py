import requests

# URLs
AUTH_URL = "http://localhost:8001"
TICKET_URL = "http://localhost:8003"

print("🔐 Probando autenticación...")

# 1. Login
print("\n1. Haciendo login...")
login_data = {
    "email_hash": "test@example.com",
    "password": "test123"
}

try:
    response = requests.post(f"{AUTH_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"Token obtenido: {token[:30]}...")
        
        # 2. Verificar token en auth-service
        print("\n2. Verificando token en auth-service...")
        verify_response = requests.post(f"{AUTH_URL}/auth/verify", data={"token": token})
        print(f"Status: {verify_response.status_code}")
        print(f"Response: {verify_response.text}")
        
        # 3. Probar ticket-service
        print("\n3. Probando ticket-service...")
        headers = {"Authorization": f"Bearer {token}"}
        ticket_response = requests.get(f"{TICKET_URL}/tickets", headers=headers)
        print(f"Status: {ticket_response.status_code}")
        print(f"Response: {ticket_response.text}")
        
    else:
        print("❌ Login falló")
        
except Exception as e:
    print(f"❌ Error: {e}") 