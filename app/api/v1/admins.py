"""Admin management API endpoints."""

from fastapi import APIRouter, Depends, Request, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from app.database import get_database
from app.dependencies import get_current_admin, get_client_ip, get_user_agent
from app.services.admin_service import AdminService
from app.schemas.admin import (
    CreateAdminRequest, UpdateAdminRequest, UpdateAdminStatusRequest,
    AdminResponse, AdminListFilters
)
from app.schemas.common import ResponseModel, PaginationParams
from app.models.admin import AdminUser
from app.core.permissions import require_permission

router = APIRouter()


@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
@require_permission("admin:write")
async def create_admin(
    request: Request,
    data: CreateAdminRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new admin user.
    
    - Requires `admin:write` permission
    - Username and email must be unique
    - All specified roles must exist
    - Password will be hashed
    - Action is logged in audit trail
    """
    admin_service = AdminService(db)
    
    # Extract session ID from token payload
    session_id = getattr(request.state, "session_id", "unknown")
    
    admin = await admin_service.create_admin(
        data=data,
        created_by=current_admin,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        session_id=session_id
    )
    
    return ResponseModel(
        success=True,
        data=AdminResponse(
            admin_id=admin.admin_id,
            username=admin.username,
            email=admin.email,
            roles=admin.roles,
            mfa_enabled=admin.mfa_enabled,
            status=admin.status,
            last_login=admin.last_login,
            created_at=admin.created_at,
            updated_at=admin.updated_at
        )
    )


@router.get("", response_model=ResponseModel, status_code=status.HTTP_200_OK)
@require_permission("admin:read")
async def list_admins(
    status: Optional[str] = Query(None, pattern="^(active|suspended|deleted)$"),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    List admin users with filters and pagination.
    
    - Requires `admin:read` permission
    - Supports filtering by status, role, and search (username/email)
    - Returns paginated results
    """
    admin_service = AdminService(db)
    
    result = await admin_service.list_admins(
        status=status,
        role=role,
        search=search,
        page=page,
        page_size=page_size
    )
    
    return ResponseModel(
        success=True,
        data=[
            AdminResponse(
                admin_id=admin.admin_id,
                username=admin.username,
                email=admin.email,
                roles=admin.roles,
                mfa_enabled=admin.mfa_enabled,
                status=admin.status,
                last_login=admin.last_login,
                created_at=admin.created_at,
                updated_at=admin.updated_at
            )
            for admin in result["items"]
        ],
        meta={
            "page": result["page"],
            "page_size": result["page_size"],
            "total": result["total"],
            "total_pages": result["total_pages"]
        }
    )


@router.get("/{admin_id}", response_model=ResponseModel, status_code=status.HTTP_200_OK)
@require_permission("admin:read")
async def get_admin(
    admin_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get admin user by ID.
    
    - Requires `admin:read` permission
    - Returns admin details
    """
    admin_service = AdminService(db)
    
    admin = await admin_service.get_admin(admin_id)
    
    return ResponseModel(
        success=True,
        data=AdminResponse(
            admin_id=admin.admin_id,
            username=admin.username,
            email=admin.email,
            roles=admin.roles,
            mfa_enabled=admin.mfa_enabled,
            status=admin.status,
            last_login=admin.last_login,
            created_at=admin.created_at,
            updated_at=admin.updated_at
        )
    )


@router.patch("/{admin_id}", response_model=ResponseModel, status_code=status.HTTP_200_OK)
@require_permission("admin:write")
async def update_admin(
    request: Request,
    admin_id: str,
    data: UpdateAdminRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update admin user.
    
    - Requires `admin:write` permission
    - Can update email and roles
    - Email must be unique if changed
    - Action is logged in audit trail
    """
    admin_service = AdminService(db)
    
    session_id = getattr(request.state, "session_id", "unknown")
    
    admin = await admin_service.update_admin(
        admin_id=admin_id,
        data=data,
        updated_by=current_admin,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        session_id=session_id
    )
    
    return ResponseModel(
        success=True,
        data=AdminResponse(
            admin_id=admin.admin_id,
            username=admin.username,
            email=admin.email,
            roles=admin.roles,
            mfa_enabled=admin.mfa_enabled,
            status=admin.status,
            last_login=admin.last_login,
            created_at=admin.created_at,
            updated_at=admin.updated_at
        )
    )


@router.patch("/{admin_id}/status", response_model=ResponseModel, status_code=status.HTTP_200_OK)
@require_permission("admin:write")
async def update_admin_status(
    request: Request,
    admin_id: str,
    data: UpdateAdminStatusRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update admin status (active/suspended).
    
    - Requires `admin:write` permission
    - Cannot change your own status
    - Reason is optional but recommended
    - Action is logged in audit trail with WARNING level
    """
    admin_service = AdminService(db)
    
    session_id = getattr(request.state, "session_id", "unknown")
    
    admin = await admin_service.update_status(
        admin_id=admin_id,
        data=data,
        updated_by=current_admin,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        session_id=session_id
    )
    
    return ResponseModel(
        success=True,
        data=AdminResponse(
            admin_id=admin.admin_id,
            username=admin.username,
            email=admin.email,
            roles=admin.roles,
            mfa_enabled=admin.mfa_enabled,
            status=admin.status,
            last_login=admin.last_login,
            created_at=admin.created_at,
            updated_at=admin.updated_at
        )
    )


@router.delete("/{admin_id}", response_model=ResponseModel, status_code=status.HTTP_200_OK)
@require_permission("admin:delete")
async def delete_admin(
    request: Request,
    admin_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Soft delete admin user.
    
    - Requires `admin:delete` permission
    - Cannot delete your own account
    - Soft delete (status set to 'deleted', deleted_at timestamp set)
    - Action is logged in audit trail with CRITICAL level
    """
    admin_service = AdminService(db)
    
    session_id = getattr(request.state, "session_id", "unknown")
    
    await admin_service.delete_admin(
        admin_id=admin_id,
        deleted_by=current_admin,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        session_id=session_id
    )
    
    return ResponseModel(
        success=True,
        data={"message": "Admin deleted successfully"}
    )
