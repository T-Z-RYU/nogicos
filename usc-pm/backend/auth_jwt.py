"""JWT issuance + FastAPI dependency for the desktop app."""
import os
import jwt
from datetime import datetime, timedelta
from fastapi import Header, HTTPException

ALGO = "HS256"


def _key() -> str:
    k = os.environ.get("JWT_SIGNING_KEY")
    if not k:
        raise RuntimeError("JWT_SIGNING_KEY not set")
    return k


def issue(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=30),
    }
    return jwt.encode(payload, _key(), algorithm=ALGO)


def require_user(authorization: str = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, _key(), algorithms=[ALGO])
    except jwt.PyJWTError as e:
        raise HTTPException(401, f"Invalid token: {e}")
    return int(payload["sub"])
