from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    BET = "bet"
    WIN = "win"
    ADJUSTMENT = "adjustment"
    BONUS = "bonus"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"

class TransactionBase(BaseModel):
    player_id: str
    amount: float
    type: TransactionType
    status: TransactionStatus = TransactionStatus.COMPLETED
    remarks: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)

class TransactionCreate(TransactionBase):
    pass

class TransactionInDB(TransactionBase):
    transaction_id: str
    amount_before: float
    amount_after: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None # Admin ID if manual adjustment
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class TransactionResponse(TransactionInDB):
    pass

class BalanceAdjustmentRequest(BaseModel):
    player_id: str
    amount: float # Positive for add, negative for subtract
    type: TransactionType = TransactionType.ADJUSTMENT
    remarks: str
