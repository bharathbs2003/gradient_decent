"""
API dependencies for authentication and authorization
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import structlog

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
from app.core.exceptions import AuthenticationError, AuthorizationError

logger = structlog.get_logger()
settings = get_settings()

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token")
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("Inactive user")
        
        return user
        
    except JWTError as e:
        logger.warning("JWT decode error", error=str(e))
        raise AuthenticationError("Invalid token")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise AuthorizationError("Admin access required")
    return current_user


async def get_creator_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get user with creator permissions"""
    if not current_user.can_create_projects:
        raise AuthorizationError("Creator access required")
    return current_user


async def get_reviewer_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get user with reviewer permissions"""
    if not current_user.can_review_translations:
        raise AuthorizationError("Reviewer access required")
    return current_user