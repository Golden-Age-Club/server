"""
Minimal Ticket model for MVP
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class TicketStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"


class Ticket(BaseModel):
    """
    Minimal Ticket Model
    No categories, priorities, or assignment.
    """
    user_id: str = Field(..., description="User ID who created the ticket")
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
