from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class PlayerStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FROZEN = "frozen"
    BANNED = "banned"

class PlayerBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    vip_level: int = Field(0, ge=0)
    status: PlayerStatus = PlayerStatus.ACTIVE
    remarks: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)

class PlayerCreate(PlayerBase):
    password: str = Field(..., min_length=6)

class PlayerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    vip_level: Optional[int] = None
    status: Optional[PlayerStatus] = None
    remarks: Optional[str] = None

class PlayerInDB(PlayerBase):
    player_id: str
    password_hash: str
    balance: float = 0.0
    total_deposits: float = 0.0
    total_withdrawals: float = 0.0
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PlayerResponse(PlayerBase):
    player_id: str
    balance: float
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
