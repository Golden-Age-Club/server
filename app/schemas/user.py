from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TelegramAuthRequest(BaseModel):
    """Request schema for Telegram authentication"""
    init_data: str = Field(..., description="Telegram WebApp initData string")
    
    class Config:
        json_schema_extra = {
            "example": {
                "init_data": "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A279058397..."
            }
        }


class UserResponse(BaseModel):
    """User profile response schema"""
    id: str = Field(..., alias="_id")
    telegram_id: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    language_code: Optional[str] = None
    balance: float
    is_active: bool
    is_premium: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "balance": 1000.0,
                "is_active": True,
                "is_premium": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class AuthResponse(BaseModel):
    """Authentication response with token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "telegram_id": 123456789,
                    "username": "johndoe",
                    "first_name": "John",
                    "balance": 0.0,
                    "is_active": True
                }
            }
        }


class UserCreateRequest(BaseModel):
    """Request schema for creating a user (admin only, or internal use)"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = "en"


class EmailLoginRequest(BaseModel):
    """Request schema for Email authentication"""
    email: str
    password: str


class EmailRegisterRequest(BaseModel):
    """Request schema for Email registration"""
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
