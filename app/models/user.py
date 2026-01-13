from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model with Telegram-specific fields"""
    telegram_id: Optional[int] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    language_code: Optional[str] = "en"
    balance: float = Field(default=0.0)
    is_active: bool = Field(default=True)
    is_premium: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "balance": 1000.0,
                "is_active": True,
                "is_premium": False
            }
        }
