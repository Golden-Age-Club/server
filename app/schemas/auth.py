"""Authentication request/response schemas."""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """Login request schema."""
    
    username: str = Field(..., min_length=3, description="Username")
    password: str = Field(..., min_length=8, description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john.doe",
                "password": "SecurePassword123!"
            }
        }


class LoginResponse(BaseModel):
    """Login response schema."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    mfa_required: bool = Field(default=False, description="MFA verification required")
    session_id: Optional[str] = Field(None, description="Session ID")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "mfa_required": False,
                "session_id": "sess_abc123"
            }
        }


class MFASetupResponse(BaseModel):
    """MFA setup response schema."""
    
    secret: str = Field(..., description="MFA secret key")
    qr_code: str = Field(..., description="QR code as base64 data URI")
    provisioning_uri: str = Field(..., description="TOTP provisioning URI")

    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
                "provisioning_uri": "otpauth://totp/SlotAdmin:john.doe?secret=JBSWY3DPEHPK3PXP&issuer=SlotAdmin"
            }
        }


class MFAVerifyRequest(BaseModel):
    """MFA verification request schema."""
    
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$", description="6-digit TOTP code")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    
    refresh_token: str = Field(..., description="JWT refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class CurrentAdminResponse(BaseModel):
    """Current admin user response schema."""
    
    admin_id: str
    username: str
    email: EmailStr
    roles: list[str]
    mfa_enabled: bool
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "admin_id": "admin_123456",
                "username": "john.doe",
                "email": "john.doe@example.com",
                "roles": ["finance_manager"],
                "mfa_enabled": True,
                "status": "active"
            }
        }
