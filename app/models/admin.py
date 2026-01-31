"""Admin user, role, and permission models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class Permission(BaseModel):
    """Permission model."""
    
    permission_id: str = Field(..., description="Unique permission identifier")
    resource: str = Field(..., description="Resource type (e.g., user, wallet)")
    action: str = Field(..., description="Action type (e.g., read, write)")
    description: str = Field(..., description="Human-readable description")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "permission_id": "user:read",
                "resource": "user",
                "action": "read",
                "description": "View user information",
                "created_at": "2026-01-30T19:00:00Z"
            }
        }


class Role(BaseModel):
    """Role model with permissions."""
    
    role_id: str = Field(..., description="Unique role identifier")
    name: str = Field(..., min_length=3, max_length=50, description="Role name")
    description: str = Field(..., description="Role description")
    permissions: List[str] = Field(default_factory=list, description="List of permission IDs")
    is_system_role: bool = Field(default=False, description="System role (cannot be deleted)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "finance_manager",
                "name": "Finance Manager",
                "description": "Manages financial operations",
                "permissions": ["wallet:read", "wallet:write", "withdrawal:approve"],
                "is_system_role": True,
                "created_at": "2026-01-30T19:00:00Z",
                "updated_at": "2026-01-30T19:00:00Z"
            }
        }


class AdminUser(BaseModel):
    """Admin user model."""
    
    admin_id: str = Field(..., description="Unique admin identifier")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password_hash: str = Field(..., description="Hashed password")
    
    mfa_secret: Optional[str] = Field(None, description="MFA secret for TOTP")
    mfa_enabled: bool = Field(default=False, description="MFA enabled status")
    
    roles: List[str] = Field(default_factory=list, description="List of role IDs")
    status: str = Field(default="active", pattern="^(active|suspended|deleted)$")
    
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    failed_login_attempts: int = Field(default=0, description="Failed login attempt counter")
    locked_until: Optional[datetime] = Field(None, description="Account lock expiration")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "admin_id": "admin_123456",
                "username": "john.doe",
                "email": "john.doe@example.com",
                "password_hash": "$2b$12$...",
                "mfa_enabled": True,
                "roles": ["finance_manager"],
                "status": "active",
                "last_login": "2026-01-30T19:00:00Z",
                "failed_login_attempts": 0,
                "created_at": "2026-01-30T19:00:00Z",
                "updated_at": "2026-01-30T19:00:00Z"
            }
        }


class AdminUserInDB(AdminUser):
    """Admin user model as stored in database."""
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
