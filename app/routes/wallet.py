from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.wallet import (
    DepositRequest, 
    WithdrawalRequest, 
    TransactionResponse,
    BalanceResponse
)
from app.services.wallet import WalletService
from app.repositories.user import UserRepository
from app.repositories.transaction import TransactionRepository
from app.dependencies import get_wallet_service, get_user_repo, get_transaction_repo
from app.middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/wallet", tags=["wallet"])

# Transaction limits (USDT)
MIN_DEPOSIT_AMOUNT = 10.0
MAX_DEPOSIT_AMOUNT = 100000.0
MIN_WITHDRAWAL_AMOUNT = 10.0
MAX_WITHDRAWAL_AMOUNT = 50000.0

@router.post("/deposit", response_model=TransactionResponse)
async def create_deposit(
    request: DepositRequest,
    req: Request,
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a USDT deposit order (requires authentication)
    
    Min amount: 10 USDT
    Max amount: 100,000 USDT
    """
    # Validate amount limits
    if request.amount < MIN_DEPOSIT_AMOUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum deposit amount is {MIN_DEPOSIT_AMOUNT} USDT"
        )
    
    if request.amount > MAX_DEPOSIT_AMOUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum deposit amount is {MAX_DEPOSIT_AMOUNT} USDT"
        )
    
    # Use authenticated user's internal ID
    user_id = str(current_user["_id"])
    
    logger.info(f"Deposit request: user={user_id}, amount={request.amount}, currency={request.currency}")
    
    transaction = await wallet_service.create_deposit(
        user_id=user_id,
        amount=request.amount,
        currency=request.currency,
        return_url=request.return_url
    )
    
    logger.info(f"✅ Deposit created: transaction_id={transaction['_id']}, user={user_id}")
    
    return TransactionResponse(
        transaction_id=transaction["_id"],
        user_id=transaction["user_id"],
        type=transaction["type"],
        amount=transaction["amount"],
        currency=transaction["currency"],
        status=transaction["status"],
        created_at=transaction["created_at"],
        payment_url=transaction.get("payment_url"),
        payment_address=transaction.get("payment_address"),
        merchant_order_id=transaction.get("merchant_order_id")
    )

@router.post("/withdraw", response_model=TransactionResponse)
async def create_withdrawal(
    request: WithdrawalRequest,
    req: Request,
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a USDT withdrawal request (requires authentication)
    
    Min amount: 10 USDT
    Max amount: 50,000 USDT
    """
    # Validate amount limits
    if request.amount < MIN_WITHDRAWAL_AMOUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum withdrawal amount is {MIN_WITHDRAWAL_AMOUNT} USDT"
        )
    
    if request.amount > MAX_WITHDRAWAL_AMOUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum withdrawal amount is {MAX_WITHDRAWAL_AMOUNT} USDT"
        )
    
    # Use authenticated user's internal ID
    user_id = str(current_user["_id"])
    
    logger.info(f"Withdrawal request: user={user_id}, amount={request.amount}, address={request.wallet_address}")
    
    transaction = await wallet_service.create_withdrawal(
        user_id=user_id,
        amount=request.amount,
        wallet_address=request.wallet_address,
        currency=request.currency
    )
    
    logger.info(f"✅ Withdrawal created: transaction_id={transaction['_id']}, user={user_id}")
    
    return TransactionResponse(
        transaction_id=transaction["_id"],
        user_id=transaction["user_id"],
        type=transaction["type"],
        amount=transaction["amount"],
        currency=transaction["currency"],
        status=transaction["status"],
        created_at=transaction["created_at"],
        merchant_order_id=transaction.get("merchant_order_id")
    )

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: dict = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo)
):
    """Get current user's balance (requires authentication)"""
    user_id = str(current_user["_id"])
    balance = await user_repo.get_balance(user_id)
    return BalanceResponse(user_id=user_id, balance=balance)

@router.get("/transactions")
async def get_transactions(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo)
):
    """Get current user's transaction history (requires authentication)"""
    user_id = str(current_user["_id"])
    transactions = await transaction_repo.get_user_transactions(user_id, limit)
    return {"user_id": user_id, "transactions": transactions}

@router.get("/transaction/{transaction_id}")
async def get_transaction_status(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo)
):
    """Get specific transaction details (requires authentication)"""
    transaction = await transaction_repo.get_by_id(transaction_id)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Verify transaction belongs to current user
    if transaction["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Access denied to this transaction")
    
    return transaction
