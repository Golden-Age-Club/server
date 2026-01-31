from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class RiskRuleType(str, Enum):
    WITHDRAWAL_FREQ = "withdrawal_freq"
    WIN_LOSS_RATIO = "win_loss_ratio"
    LARGE_BET = "large_bet"
    ABNORMAL_PATTERN = "abnormal_pattern"

class RiskAction(str, Enum):
    FLAG = "flag"
    REVIEW = "review"
    FREEZE = "freeze"

class RiskRule(BaseModel):
    rule_id: str
    type: RiskRuleType
    threshold: float
    time_window_minutes: Optional[int] = None
    action: RiskAction
    is_active: bool = True
    description: str

class RiskAlert(BaseModel):
    alert_id: str
    player_id: str
    rule_id: str
    rule_type: RiskRuleType
    value_detected: float
    status: str = "pending" # pending, cleared, confirmed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    remarks: Optional[str] = None
