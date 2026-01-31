"""Admin management request/response schemas."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class CreateAdminRequest(BaseModel):
    """Create admin request schema."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    roles: List[str] = Field(..., min_length=1, description="List of role IDs")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "jane.smith",
                "email": "jane.smith@example.com",
                "password": "SecurePassword123!",
                "roles": ["customer_support"]
            }
        }


class UpdateAdminRequest(BaseModel):
    """Update admin request schema."""
    
    email: Optional[EmailStr] = Field(None, description="Email address")
    roles: Optional[List[str]] = Field(None, description="List of role IDs")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jane.smith.new@example.com",
                "roles": ["customer_support", "analyst"]
            }
        }


class UpdateAdminStatusRequest(BaseModel):
    """Update admin status request schema."""
    
    status: str = Field(..., pattern="^(active|suspended)$", description="New status")
    reason: Optional[str] = Field(None, description="Reason for status change")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "suspended",
                "reason": "Policy violation"
            }
        }


class AdminResponse(BaseModel):
    """Admin user response schema."""
    
    admin_id: str
    username: str
    email: EmailStr
    roles: List[str]
    mfa_enabled: bool
    status: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "admin_id": "admin_123456",
                "username": "jane.smith",
                "email": "jane.smith@example.com",
                "roles": ["customer_support"],
                "mfa_enabled": False,
                "status": "active",
                "last_login": "2026-01-30T19:00:00Z",
                "created_at": "2026-01-29T10:00:00Z",
                "updated_at": "2026-01-30T19:00:00Z"
            }
        }


class AdminListFilters(BaseModel):
    """Admin list filter parameters."""
    
    status: Optional[str] = Field(None, pattern="^(active|suspended|deleted)$")
    role: Optional[str] = Field(None, description="Filter by role ID")
    search: Optional[str] = Field(None, description="Search by username or email")
