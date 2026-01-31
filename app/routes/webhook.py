from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Header, Depends
from app.models.transaction import TransactionType, TransactionStatus
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.services.ccpayment import get_payment_provider, PaymentProvider
from app.dependencies import get_transaction_repo, get_user_repo
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhook"])

@router.post("/api/webhook/ccpayment")
async def ccpayment_webhook(
    request: Request,
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    payment_provider: PaymentProvider = Depends(get_payment_provider),
    timestamp: str = Header(...),
    sign: str = Header(...)
):
    """Webhook endpoint to receive payment notifications from CCPayment"""
    body = await request.json()
    
    logger.info(f"Webhook received: order_id={body.get('merchant_order_id')}, status={body.get('order_status')}")
    
    # Verify webhook signature
    if not payment_provider.verify_webhook_signature(timestamp, sign, body):
        logger.warning(f"⚠️ Invalid webhook signature for order: {body.get('merchant_order_id')}")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    merchant_order_id = body.get("merchant_order_id")
    order_status = body.get("order_status")
    
    # Get transaction from database
    transaction = await transaction_repo.get_by_merchant_order_id(merchant_order_id)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction_id = transaction["_id"]
    user_id = transaction["user_id"]
    amount = transaction["amount"]
    transaction_type = transaction["type"]
    
    # Handle deposit confirmation
    if transaction_type == TransactionType.DEPOSIT:
        if order_status == "paid" or order_status == "confirmed":
            logger.info(f"Processing deposit confirmation: user={user_id}, amount={amount}")
            await user_repo.update_balance(user_id, amount)
            
            await transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                webhook_data=body
            )
            logger.info(f"✅ Deposit completed: transaction_id={transaction_id}, user={user_id}")
            
        elif order_status == "expired" or order_status == "failed":
            await transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.FAILED,
                webhook_data=body
            )
    
    # Handle withdrawal confirmation
    elif transaction_type == TransactionType.WITHDRAWAL:
        if order_status == "success" or order_status == "completed":
            logger.info(f"✅ Withdrawal completed: transaction_id={transaction_id}, user={user_id}")
            await transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                webhook_data=body
            )
            
        elif order_status == "failed":
            # Refund the balance
            logger.warning(f"⚠️ Withdrawal failed, refunding: user={user_id}, amount={amount}")
            await user_repo.update_balance(user_id, amount)
            
            await transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.FAILED,
                webhook_data=body
            )
    
    return {"status": "success"}