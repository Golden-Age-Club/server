"""Audit log model."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.admin import PyObjectId


class AuditLog(BaseModel):
    """Audit log model for tracking admin actions."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(..., pattern="^(INFO|WARN|CRITICAL)$", description="Log level")
    
    admin_id: str = Field(..., description="Admin user ID who performed the action")
    admin_username: str = Field(..., description="Admin username")
    
    action: str = Field(..., description="Action performed (e.g., admin.create, user.freeze)")
    resource_type: str = Field(..., description="Resource type affected")
    resource_id: str = Field(..., description="Resource ID affected")
    
    ip_address: str = Field(..., description="Client IP address")
    user_agent: str = Field(..., description="Client user agent")
    
    changes: Dict[str, Any] = Field(default_factory=dict, description="Before/after state")
    reason: Optional[str] = Field(None, description="Reason for action")
    session_id: str = Field(..., description="Session ID")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-01-30T19:00:00Z",
                "level": "INFO",
                "admin_id": "admin_123456",
                "admin_username": "john.doe",
                "action": "user.freeze",
                "resource_type": "user",
                "resource_id": "user_67890",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "changes": {
                    "old_status": "active",
                    "new_status": "frozen"
                },
                "reason": "Suspicious betting pattern",
                "session_id": "sess_abc123"
            }
        }


class AuditLogInDB(AuditLog):
    """Audit log model as stored in database."""
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
