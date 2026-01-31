"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as redis

from app.database import get_database
from app.dependencies import get_redis, get_current_admin, get_client_ip, get_user_agent
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest, LoginResponse, MFASetupResponse, MFAVerifyRequest,
    RefreshTokenRequest, CurrentAdminResponse
)
from app.schemas.common import ResponseModel
from app.models.admin import AdminUser

router = APIRouter()


@router.post("/login", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Admin login endpoint.
    
    - Authenticates admin with username and password
    - Returns JWT access and refresh tokens
    - Returns user object with role and permissions (frontend format)
    - Indicates if MFA verification is required
    - Rate limited to 5 attempts per 15 minutes per IP
    """
    from app.services.permission_mapper import get_frontend_permissions, get_primary_role_alias
    
    auth_service = AuthService(db, redis_client)
    
    # Authenticate admin
    admin = await auth_service.authenticate_admin(data.username, data.password)
    
    # Create session
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    session_data = await auth_service.create_session(admin, ip_address, user_agent)
    
    # Get frontend-compatible permissions
    frontend_permissions = await get_frontend_permissions(admin, db)
    primary_role = get_primary_role_alias(admin.roles)
    
    # Add user object to response
    session_data["user"] = {
        "admin_id": admin.admin_id,
        "username": admin.username,
        "email": admin.email,
        "role": primary_role,
        "roles": admin.roles,
        "permissions": frontend_permissions,
        "mfa_enabled": admin.mfa_enabled,
        "status": admin.status
    }
    
    return ResponseModel(
        success=True,
        data=session_data
    )


@router.post("/mfa/setup", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def setup_mfa(
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Set up MFA for current admin.
    
    - Generates MFA secret and QR code
    - Returns secret, QR code image (base64), and provisioning URI
    - MFA not enabled until first code is verified
    """
    auth_service = AuthService(db, redis_client)
    
    mfa_data = await auth_service.setup_mfa(current_admin.admin_id)
    
    return ResponseModel(
        success=True,
        data=mfa_data
    )


@router.post("/mfa/enable", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def enable_mfa(
    data: MFAVerifyRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Enable MFA after verifying first code.
    
    - Verifies TOTP code
    - Enables MFA for admin account
    - Future logins will require MFA verification
    """
    auth_service = AuthService(db, redis_client)
    
    await auth_service.enable_mfa(current_admin.admin_id, data.code)
    
    return ResponseModel(
        success=True,
        data={"message": "MFA enabled successfully"}
    )


@router.post("/mfa/verify", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def verify_mfa(
    data: MFAVerifyRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Verify MFA code during login.
    
    - Validates TOTP code
    - Required for admins with MFA enabled
    """
    auth_service = AuthService(db, redis_client)
    
    is_valid = await auth_service.verify_mfa(current_admin.admin_id, data.code)
    
    return ResponseModel(
        success=True,
        data={"valid": is_valid}
    )


@router.post("/refresh", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Refresh access token using refresh token.
    
    - Validates refresh token
    - Returns new access and refresh tokens (token rotation)
    - Old refresh token is invalidated
    """
    auth_service = AuthService(db, redis_client)
    
    tokens = await auth_service.refresh_session(data.refresh_token)
    
    return ResponseModel(
        success=True,
        data=tokens
    )


@router.post("/logout", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Logout and invalidate session.
    
    - Invalidates current session
    - Removes session from Redis
    - Tokens will no longer be valid
    """
    auth_service = AuthService(db, redis_client)
    
    # Extract session ID from request state (set by auth middleware)
    session_id = getattr(request.state, "session_id", None)
    
    if session_id:
        await auth_service.logout(session_id)
    
    return ResponseModel(
        success=True,
        data={"message": "Logged out successfully"}
    )


@router.get("/me", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_current_user(
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get current authenticated admin user information.
    
    - Returns admin profile with frontend-compatible permissions
    - Requires valid JWT token
    """
    from app.services.permission_mapper import get_frontend_permissions, get_primary_role_alias
    
    # Get frontend-compatible permissions
    frontend_permissions = await get_frontend_permissions(current_admin, db)
    primary_role = get_primary_role_alias(current_admin.roles)
    
    return ResponseModel(
        success=True,
        data={
            "admin_id": current_admin.admin_id,
            "username": current_admin.username,
            "email": current_admin.email,
            "role": primary_role,
            "roles": current_admin.roles,
            "permissions": frontend_permissions,
            "mfa_enabled": current_admin.mfa_enabled,
            "status": current_admin.status,
            "last_login": current_admin.last_login
        }
    )
