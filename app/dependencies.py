from fastapi import Depends
from app.core.database import get_database
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.services.ccpayment import get_payment_provider, PaymentProvider
from app.services.wallet import WalletService

async def get_transaction_repo(db = Depends(get_database)):
    return TransactionRepository(db)

async def get_user_repo(db = Depends(get_database)):
    return UserRepository(db)

async def get_wallet_service(
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    return WalletService(transaction_repo, user_repo, payment_provider)

# Support System Dependencies
from app.repositories.ticket import TicketRepository
from app.repositories.support_message import SupportMessageRepository

async def get_ticket_repo(db=Depends(get_database)):
    return TicketRepository(db)

async def get_message_repo(db=Depends(get_database)):
    return SupportMessageRepository(db)
