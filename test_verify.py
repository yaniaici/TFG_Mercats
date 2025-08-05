import requests

# URLs
AUTH_URL = "http://localhost:8001"

print("🔐 Probando verificación de token...")

# 1. Login
print("\n1. Haciendo login...")
login_data = {
    "email_hash": "nuevo@test.com",
    "password": "password123"
}

try:
    response = requests.post(f"{AUTH_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"Token obtenido: {token[:30]}...")
        
        # 2. Verificar token en auth-service
        print("\n2. Verificando token en auth-service...")
        verify_data = {"token": token}
        verify_response = requests.post(f"{AUTH_URL}/auth/verify", json=verify_data)
        print(f"Status: {verify_response.status_code}")
        print(f"Response: {verify_response.text}")
        
    else:
        print("❌ Login falló")
        
except Exception as e:
    print(f"❌ Error: {e}") 