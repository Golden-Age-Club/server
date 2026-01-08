from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Header
from app.config import get_settings
from app.repositories.user import UserRepository
from app.dependencies import get_user_repo
from app.utils.telegram_auth import validate_and_parse_telegram_data

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
    telegram_id = payload.get("telegram_id")
    
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Get user from database
    user = await user_repo.get_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    return user


async def get_current_user_from_telegram(
    telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    user_repo: UserRepository = Depends(get_user_repo)
) -> Dict:
    """
    Get current user from Telegram initData header (for direct Telegram WebApp integration)
    
    Args:
        telegram_init_data: Telegram initData from X-Telegram-Init-Data header
        user_repo: User repository dependency
    
    Returns:
        User dictionary from database
    
    Raises:
        HTTPException: If authentication fails
    """
    # Skip validation in testing mode
    if settings.TESTING_MODE:
        # In testing mode, expect a simple telegram_id in the header
        try:
            telegram_id = int(telegram_init_data)
            user = await user_repo.get_by_telegram_id(telegram_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid telegram_id in testing mode")
    
    # Validate Telegram initData
    user_data = validate_and_parse_telegram_data(telegram_init_data, settings.TELEGRAM_BOT_TOKEN)
    telegram_id = user_data.get("telegram_id")
    
    # Get user from database
    user = await user_repo.get_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found. Please register first.")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    return user


# Alias for the default authentication method (can switch between token and telegram)
async def get_current_user(
    user_repo: UserRepository = Depends(get_user_repo),
    authorization: Optional[str] = Header(None),
    telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data")
) -> Dict:
    """
    Get current user from either JWT token or Telegram initData
    Tries JWT first, then falls back to Telegram initData
    
    Args:
        user_repo: User repository dependency
        authorization: Optional Authorization header with Bearer token
        telegram_init_data: Optional Telegram initData header
    
    Returns:
        User dictionary from database
    
    Raises:
        HTTPException: If authentication fails
    """
    # Try JWT token first
    if authorization and authorization.startswith("Bearer "):
        return await get_current_user_from_token(authorization, user_repo)
    
    # Try Telegram initData
    if telegram_init_data:
        return await get_current_user_from_telegram(telegram_init_data, user_repo)
    
    # No authentication provided
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide either Authorization header or X-Telegram-Init-Data header"
    )
