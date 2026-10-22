"""Authentication services, password hashing, and JWT handling."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database import get_db
from backend.models import User

settings = get_settings()
security = HTTPBearer(auto_error=False)

# Modern password hashing with pwdlib Argon2
try:
    from pwdlib import PasswordHash
    _password_hash = PasswordHash.recommended()

    def hash_password(password: str) -> str:
        return _password_hash.hash(password)

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return _password_hash.verify(plain_password, hashed_password)

except Exception:
    import hashlib

    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Retrieve the authenticated user from the Bearer JWT token."""
    if not credentials:
        return None

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if not user_id:
            return None
    except jwt.PyJWTError:
        return None

    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def require_authenticated_user(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """Enforce authentication requirement."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
