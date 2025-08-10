import httpx
import os
from fastapi import HTTPException, status

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")


async def get_user_me(token: str) -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{AUTH_SERVICE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
            if resp.status_code == 200:
                return resp.json()
            return None
    except Exception:
        return None


async def require_admin(token: str) -> dict:
    user = await get_user_me(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere rol admin")
    return user


