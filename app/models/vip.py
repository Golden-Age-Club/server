from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class VIPTierConfig(BaseModel):
    level: int = Field(..., ge=0)
    name: str
    min_deposits: float = 0.0
    min_bet_amount: float = 0.0
    benefits: List[str] = []
    
    model_config = ConfigDict(use_enum_values=True)

class VIPConfigRequest(BaseModel):
    tiers: List[VIPTierConfig]

class VIPLevelAdjustmentRequest(BaseModel):
    player_id: str
    new_level: int = Field(..., ge=0)
    reason: str
