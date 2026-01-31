"""FastAPI dependency injection functions."""

from typing import Optional
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as redis

from app.config import settings
from app.database import get_database
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError
from app.models.admin import AdminUser


# Security scheme
security = HTTPBearer()


# Redis connection pool
redis_pool: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis connection."""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_pool


async def get_current_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> AdminUser:
    """Get current authenticated admin user from JWT token."""
    
    token = credentials.credentials
    
    try:
        # Decode token
        payload = decode_token(token)
        
        # Verify token type
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type")
        
        # Get admin ID from payload
        admin_id = payload.get("sub")
        if not admin_id:
            raise AuthenticationError("Invalid token payload")
        
        # Fetch admin from database
        admin_doc = await db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc:
            raise AuthenticationError("Admin user not found")
        
        # Convert to AdminUser model
        admin = AdminUser(**admin_doc)
        
        # Check if admin is active
        if admin.status != "active":
            raise AuthenticationError(f"Admin account is {admin.status}")
        
        # Store admin in request state for audit middleware
        request.state.admin = admin
        
        return admin
        
    except AuthenticationError:
        raise
    except Exception as e:
        raise AuthenticationError(f"Authentication failed: {str(e)}")


async def get_optional_admin(
    authorization: Optional[str] = Header(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Optional[AdminUser]:
    """Get current admin user if authenticated, None otherwise."""
    
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = decode_token(token)
        admin_id = payload.get("sub")
        
        if admin_id:
            admin_doc = await db.admin_users.find_one({"admin_id": admin_id})
            if admin_doc and admin_doc.get("status") == "active":
                return AdminUser(**admin_doc)
    except:
        pass
    
    return None


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    # Check for X-Forwarded-For header (proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Extract user agent from request."""
    return request.headers.get("User-Agent", "unknown")
