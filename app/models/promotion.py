from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class PromotionType(str, Enum):
    DEPOSIT_MATCH = "deposit_match"
    WELCOME = "welcome"
    REBATE = "rebate"
    FREE_SPINS = "free_spins"

class PromotionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

class Promotion(BaseModel):
    promo_id: str
    name: str
    description: str
    type: PromotionType
    bonus_percent: float = 0.0
    max_bonus: Optional[float] = None
    min_deposit: float = 0.0
    wagering_requirement: int = 30 # Multiplier
    status: PromotionStatus = PromotionStatus.INACTIVE
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
