from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class GameStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class GameBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(..., min_length=1, max_length=50)
    rtp: float = Field(..., ge=0, le=100, description="Return to Player percentage")
    status: GameStatus = GameStatus.ACTIVE
    image_url: Optional[str] = None
    description: Optional[str] = None
    min_bet: float = Field(0.1, ge=0)
    max_bet: float = Field(100.0, ge=0)

    model_config = ConfigDict(use_enum_values=True)

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = Field(None, min_length=1, max_length=50)
    rtp: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[GameStatus] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    min_bet: Optional[float] = None
    max_bet: Optional[float] = None

class GameInDB(GameBase):
    game_id: str
    created_at: datetime
    updated_at: datetime

class GameResponse(GameInDB):
    pass
