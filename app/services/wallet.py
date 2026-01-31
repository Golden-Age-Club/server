import time
from fastapi import HTTPException
from app.models.transaction import TransactionType, TransactionStatus
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.services.ccpayment import PaymentProvider
from app.config import get_settings

settings = get_settings()

class WalletService:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        user_repo: UserRepository,
        payment_provider: PaymentProvider
    ):
        self.transaction_repo = transaction_repo
        self.user_repo = user_repo
        self.payment_provider = payment_provider
    
    async def create_deposit(
        self,
        user_id: str,
        amount: float,
        currency: str,
        return_url: str = None
    ):
        # Generate unique merchant order ID
        merchant_order_id = f"DEP-{int(time.time())}-{user_id}"
        
        # Create transaction in database
        transaction_id = await self.transaction_repo.create(
            user_id=user_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            currency=currency,
            merchant_order_id=merchant_order_id
        )
        
        try:
            # Create payment order
            notify_url = settings.WEBHOOK_URL
            
            payment_data = await self.payment_provider.create_payment_order(
                order_id=merchant_order_id,
                amount=amount,
                currency=currency,
                notify_url=notify_url,
                return_url=return_url
            )
            
            # Update transaction with payment info
            await self.transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.PENDING,
                payment_url=payment_data.get("payment_url"),
                payment_address=payment_data.get("crypto_address"),
                ccpayment_order_id=payment_data.get("order_id")
            )
            
            transaction = await self.transaction_repo.get_by_id(transaction_id)
            return transaction
            
        except HTTPException:
            await self.transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.FAILED,
                error_message="Payment Provider Error"
            )
            raise
        except Exception as e:
            await self.transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.FAILED,
                error_message=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Wallet Deposit Error: {str(e)}")
    
    async def create_withdrawal(
        self,
        user_id: str,
        amount: float,
        wallet_address: str,
        currency: str
    ):
        # Atomically deduct from balance and check sufficient funds
        try:
            new_balance = await self.user_repo.deduct_balance(user_id, amount)
        except HTTPException:
            raise
        
        # Generate unique merchant order ID
        merchant_order_id = f"WD-{int(time.time())}-{user_id}"
        
        # Create transaction
        transaction_id = await self.transaction_repo.create(
            user_id=user_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            currency=currency,
            merchant_order_id=merchant_order_id,
            wallet_address=wallet_address
        )
        
        try:
            # Create withdrawal with payment provider
            notify_url = settings.WEBHOOK_URL
            
            withdrawal_data = await self.payment_provider.create_withdrawal(
                withdraw_id=merchant_order_id,
                wallet_address=wallet_address,
                amount=amount,
                currency=currency,
                notify_url=notify_url
            )
            
            # Update transaction status
            await self.transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.PROCESSING,
                ccpayment_withdraw_id=withdrawal_data.get("withdraw_id")
            )
            
            transaction = await self.transaction_repo.get_by_id(transaction_id)
            return transaction
            
        except Exception as e:
            # Refund the balance since withdrawal failed
            await self.user_repo.update_balance(user_id, amount)
            await self.transaction_repo.update_status(
                transaction_id=transaction_id,
                status=TransactionStatus.FAILED,
                error_message=str(e)
            )
            raise HTTPException(status_code=500, detail=str(e))