from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status
from typing import Optional

# Demo user (αργότερα μπορείς να το κάνεις json/db)
USERS = {
    "demo@demo.com": {"password": "1234"}
}

JWT_SECRET = "CHANGE_ME_SUPER_SECRET"  # άλλαξέ το πριν την παράδοση
JWT_ALG = "HS256"
ACCESS_TTL_MIN = 15
REFRESH_TTL_DAYS = 7


def verify_user(email: str, password: str) -> bool:
    u = USERS.get(email)
    return bool(u and u["password"] == password)


def _create_token(sub: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_access_token(sub: str) -> str:
    return _create_token(sub, "access", timedelta(minutes=ACCESS_TTL_MIN))


def create_refresh_token(sub: str) -> str:
    return _create_token(sub, "refresh", timedelta(days=REFRESH_TTL_DAYS))


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def require_access_token(auth_header: Optional[str]) -> str:
    """
    Παίρνει Authorization header 'Bearer <token>' και επιστρέφει sub (email).
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
        )
    token = auth_header.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not an access token",
        )
    return payload["sub"]
