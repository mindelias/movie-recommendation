# utils/security.py
import os
import jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from .config import  settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generate a JWT access token with optional expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        print(f"expire: {expire}")  # Add this line to print the value of expire)
    
    to_encode.update({"exp": expire})
    # ensure every custom value is JSON serialisable
    if "user_id" in to_encode:
        to_encode["user_id"] = str(to_encode["user_id"])     # UUID → str
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token,  settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )