from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class Currency(str, Enum):
    USDT_TRC20 = "USDT.TRC20"
    USDT_ERC20 = "USDT.ERC20"
    USDT_BEP20 = "USDT.BEP20"

class Transaction(BaseModel):
    user_id: str
    type: TransactionType
    amount: float
    currency: str
    status: TransactionStatus
    merchant_order_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    payment_url: Optional[str] = None
    payment_address: Optional[str] = None
    wallet_address: Optional[str] = None
    ccpayment_order_id: Optional[str] = None
    error_message: Optional[str] = None