from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.transaction import Currency, TransactionType, TransactionStatus

class DepositRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount in USDT")
    currency: Currency = Currency.USDT_TRC20
    return_url: Optional[str] = None

class WithdrawalRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount in USDT")
    wallet_address: str
    currency: Currency = Currency.USDT_TRC20

class TransactionResponse(BaseModel):
    transaction_id: str
    user_id: str
    type: TransactionType
    amount: float
    currency: str
    status: TransactionStatus
    created_at: datetime
    payment_url: Optional[str] = None
    payment_address: Optional[str] = None

class BalanceResponse(BaseModel):
    user_id: str
    balance: float