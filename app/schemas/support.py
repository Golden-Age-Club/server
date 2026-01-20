"""
Minimal Request/Response Schemas for Support MVP
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.ticket import TicketStatus


# --- REQUESTS ---

class CreateTicketRequest(BaseModel):
    """Initial message is required to create a ticket"""
    content: str = Field(..., min_length=1, max_length=4000)


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


# --- RESPONSES ---

class TicketResponse(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    status: TicketStatus
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class MessageResponse(BaseModel):
    id: str = Field(..., alias="_id")
    sender_id: str
    sender_role: str
    content: str
    created_at: datetime

    class Config:
        populate_by_name = True
