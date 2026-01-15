"""
Minimal Support Message model for MVP
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class SenderRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SupportMessage(BaseModel):
    """
    Minimal Message Model
    Plain text only. No attachments.
    """
    ticket_id: str = Field(..., description="Parent Ticket ID")
    sender_id: str = Field(..., description="ID of the sender")
    sender_role: SenderRole = Field(..., description="Role of sender: user/admin")
    content: str = Field(..., min_length=1, max_length=4000, description="Plain text content")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
