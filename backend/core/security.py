from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import bcrypt
from app.core.config import settings

def hash_password(pw: str) -> str:
    return bcrypt.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.verify(pw, hashed)

def create_jwt(sub: str, scopes: list[str]) -> str:
    exp = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    payload = {"sub": sub, "scopes": scopes, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
