from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, TokenOut
from app.core.security import create_jwt, verify_password
from app.db.session import get_db
from app.db.models import User
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_jwt(str(user.id), ["agents:invoke","admin"])
    return {"access_token": token, "expires_in": settings.JWT_EXPIRES_MIN*60}
