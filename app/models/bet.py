from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class BetStatus(str, Enum):
    ONGOING = "ongoing"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"

class BetBase(BaseModel):
    player_id: str
    game_id: str
    amount: float = Field(..., ge=0)
    win_amount: float = Field(0.0, ge=0)
    multiplier: float = Field(0.0, ge=0)
    status: BetStatus = BetStatus.ONGOING
    
    model_config = ConfigDict(use_enum_values=True)

class BetCreate(BetBase):
    pass

class BetInDB(BetBase):
    bet_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BetResponse(BetInDB):
    pass
