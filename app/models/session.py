"""Admin session model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AdminSession(BaseModel):
    """Admin session model for Redis storage."""
    
    session_id: str = Field(..., description="Unique session identifier")
    admin_id: str = Field(..., description="Admin user ID")
    access_token_hash: str = Field(..., description="Hashed access token")
    refresh_token_hash: str = Field(..., description="Hashed refresh token")
    
    ip_address: str = Field(..., description="Client IP address")
    user_agent: str = Field(..., description="Client user agent")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Session expiration time")
    last_activity: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "admin_id": "admin_123456",
                "access_token_hash": "sha256hash...",
                "refresh_token_hash": "sha256hash...",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "created_at": "2026-01-30T19:00:00Z",
                "expires_at": "2026-01-30T27:00:00Z",
                "last_activity": "2026-01-30T19:00:00Z"
            }
        }
