from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Header
from app.config import get_settings
from app.repositories.user import UserRepository
from app.dependencies import get_user_repo
# from app.utils.telegram_auth import validate_and_parse_telegram_data

settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt


def verify_access_token(token: str) -> Dict:
    """
    Verify and decode a JWT access token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


async def get_current_user_from_token(
    authorization: str = Header(...),
    user_repo: UserRepository = Depends(get_user_repo)
) -> Dict:
    """
    Get current user from JWT token in Authorization header
    
    Args:
        authorization: Authorization header with Bearer token
        user_repo: User repository dependency
    
    Returns:
        User dictionary from database
    
    Raises:
        HTTPException: If authentication fails
    """
    # Check if authorization header has Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.replace("Bearer ", "")
    
    # Verify token
    payload = verify_access_token(token)
    user_id = payload.get("user_id")
    telegram_id = payload.get("telegram_id")
    
    user = None
    if user_id:
        user = await user_repo.get_by_id(user_id)
    elif telegram_id:
        # Fallback for old tokens
        user = await user_repo.get_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found or invalid token payload")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    if user.get("_id") is not None:
        user["_id"] = str(user["_id"])
    
    return user




async def get_current_user(
    user_repo: UserRepository = Depends(get_user_repo),
    authorization: Optional[str] = Header(None)
) -> Dict:
    """
    Get current user from JWT token.
    Standardized method for all platform operations.
    
    Args:
        user_repo: User repository dependency
        authorization: Optional Authorization header with Bearer token
    
    Returns:
        User dictionary from database
    
    Raises:
        HTTPException: If authentication fails
    """
    if authorization and authorization.startswith("Bearer "):
        return await get_current_user_from_token(authorization, user_repo)
    
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide Authorization: Bearer <token>"
    )
