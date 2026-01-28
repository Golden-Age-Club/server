from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import hmac
import hashlib
import urllib.parse
import json
from app.config import get_settings
from app.repositories.user import UserRepository
from app.repositories.transaction import TransactionRepository
from app.dependencies import get_user_repo, get_transaction_repo
from app.middleware.auth import verify_access_token
from app.models.transaction import TransactionType, TransactionStatus
import base64

router = APIRouter(tags=["callback"])
settings = get_settings()
logger = logging.getLogger(__name__)

class UnifiedCallbackRequest(BaseModel):
    cmd: str
    player_token: str
    currencyId: str
    request_time: int
    signature: str

from datetime import datetime
import uuid

@router.post("/api/callback")
async def unified_callback(
    request: Request, 
    user_repo: UserRepository = Depends(get_user_repo),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo)
):
     body = await request.json()
    print(f"Callback Body: {body}")
    # try:
    #     body = await request.json()
    #     print(f"Callback Body: {body}")
    #     cmd = body.get('cmd')
    #     player_token = body.get('player_token')
    

    #     # 1. FLEXIBLE TOKEN DECODING
    #     user_id = None
    #     try:
    #         # Try your JWT logic first
    #         payload = verify_access_token(player_token)
    #         # Support both 'user_id' (from user input) and 'sub' (standard JWT)
    #         user_id = payload.get("user_id") or payload.get("sub")
    #     except Exception as e:
    #         # If JWT fails, try Base64 (like the MGC sample)
    #         try:
    #             decoded = base64.b64decode(player_token).decode('utf-8')
    #             # Check if decoded is JSON or just user ID
    #             if decoded.startswith('{'):
    #                 user_id = json.loads(decoded).get('player_id') or json.loads(decoded).get('user_id')
    #             else:
    #                 user_id = decoded
    #         except:
    #             logger.error(f"Could not decode player_token via JWT or Base64: {e}")

    #     if not user_id:
    #         return {"result": False, "err_desc": "Player Not Found", "err_code": 2}

    #     user = await user_repo.get_by_id(user_id)
    #     if not user:
    #          # Try telegram_id if user_id lookup failed
    #         if str(user_id).isdigit():
    #             user = await user_repo.get_by_telegram_id(int(user_id))
            
    #         if not user:
    #             return {"result": False, "err_desc": "Player Not Found", "err_code": 2}

    #     # 2. HANDLE COMMANDS
    #     if cmd == 'getPlayerInfo' or cmd == 'getBalance':
    #         logger.info(f"Returning Player Info for {user_id}")
    #         return {
    #             "result": True,
    #             "err_desc": "OK",
    #             "err_code": 0,
    #             "currency": "USD",
    #             "balance": float(user.get("balance", 0)),
    #             "display_name": user.get("username", "Player"),
    #             "gender": "m",
    #             "country": "US",
    #             "player_id": str(user["_id"])
    #         }

    #     elif cmd == 'deposit':
    #         # "deposit" usually means the player WON (money comes IN to the wallet)
    #         amount = float(body.get('winAmount', 0))
    #         if amount < 0:
    #              amount = 0
            
    #         before_balance = float(user.get("balance", 0))
    #         new_balance = await user_repo.update_balance(str(user["_id"]), amount)
            
    #         # Use provided transactionId or generate one
    #         tx_id = body.get('transactionId') or f"dep_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}"
            
    #         # Record Transaction
    #         await transaction_repo.create(
    #             user_id=str(user["_id"]),
    #             transaction_type=TransactionType.GAME_WIN,
    #             amount=amount,
    #             currency=body.get('currencyId', 'USD'),
    #             status=TransactionStatus.COMPLETED,
    #             merchant_order_id=tx_id,
    #             game_id=body.get('gameId'),
    #             round_id=body.get('roundId'),
    #             bet_info=body.get('betInfo')
    #         )

    #         # Update User Stats
    #         await user_repo.update_game_stats(str(user["_id"]), win_amount=amount)
            
    #         return {
    #             "result": True,
    #             "err_desc": "OK",
    #             "err_code": 0,
    #             "balance": new_balance,
    #             "before_balance": before_balance,
    #             "transactionId": tx_id
    #         }

    #     elif cmd == 'withdraw':
    #         # "withdraw" usually means the player BET (money goes OUT of the wallet)
    #         amount = float(body.get('betAmount', 0))
    #         # Safety: ensure amount is non-negative
    #         if amount < 0:
    #             logger.warning(f"Negative bet amount received: {amount}. Treating as 0.")
    #             amount = 0
            
    #         before_balance = float(user.get("balance", 0))
    #         try:
    #             if amount > 0:
    #                 new_balance = await user_repo.deduct_balance(str(user["_id"]), amount)
    #             else:
    #                 new_balance = before_balance
    #         except HTTPException:
    #             return {"result": False, "err_desc": "Insufficient balance", "err_code": 100}
                
    #         tx_id = body.get('transactionId') or f"wd_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}"
            
    #         # Record Transaction
    #         await transaction_repo.create(
    #             user_id=str(user["_id"]),
    #             transaction_type=TransactionType.GAME_BET,
    #             amount=amount,
    #             currency=body.get('currencyId', 'USD'),
    #             status=TransactionStatus.COMPLETED,
    #             merchant_order_id=tx_id,
    #             game_id=body.get('gameId'),
    #             round_id=body.get('roundId'),
    #             bet_info=body.get('betInfo')
    #         )

    #         # Update User Stats
    #         await user_repo.update_game_stats(str(user["_id"]), bet_amount=amount)
            
    #         return {
    #             "result": True,
    #             "err_desc": "OK",
    #             "err_code": 0,
    #             "balance": new_balance,
    #             "before_balance": before_balance,
    #             "transactionId": tx_id
    #         }

    #     elif cmd == 'rollback':
    #         # Rollback: Refund a previous transaction (usually a bet/withdraw)
    #         # Log shows: 'transactionId', but amount might not be explicit in simple rollback
    #         # However, typically rollback includes the amount to refund or we might need to look it up.
    #         # Based on logs provided, rollback doesn't show amount, but let's check standard PG/MGC logic.
    #         # Usually rollback provides 'betAmount' or 'amount' to refund.
    #         # If not present, we might need to assume it's full refund or handle 0 safely.
    #         # Let's check if 'betAmount' or 'amount' is in body for rollback.
    #         # If strictly following logs: {'cmd': 'rollback', ...} no amount shown in your snippet.
    #         # But normally rollback cancels a bet, so we should ADD back the money.
            
    #         # SAFELY GET AMOUNT:
    #         amount = float(body.get('betAmount', 0)) # Try betAmount first (common in bet cancellations)
    #         if amount == 0:
    #              amount = float(body.get('amount', 0)) # Fallback generic amount
            
    #         before_balance = float(user.get("balance", 0))
    #         new_balance = await user_repo.update_balance(str(user["_id"]), amount)
            
    #         tx_id = body.get('transactionId') or f"rb_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}"
            
    #          # Record Transaction
    #         await transaction_repo.create(
    #             user_id=str(user["_id"]),
    #             transaction_type=TransactionType.GAME_REFUND,
    #             amount=amount,
    #             currency=body.get('currencyId', 'USD'),
    #             status=TransactionStatus.COMPLETED,
    #             merchant_order_id=tx_id,
    #             game_id=body.get('gameId'),
    #             round_id=body.get('roundId'),
    #             bet_info=body.get('betInfo')
    #         )

    #         return {
    #             "result": True,
    #             "err_desc": "OK",
    #             "err_code": 0,
    #             "balance": new_balance,
    #             "before_balance": before_balance,
    #             "transactionId": tx_id
    #         }

    #     # 3. ACKNOWLEDGE OTHERS
    #     elif cmd in ['bet', 'win', 'refund']:
    #         # Fallback for other commands if any
    #         return {
    #             "result": True,
    #             "err_desc": "OK",
    #             "err_code": 0,
    #             "balance": float(user.get("balance", 0))
    #         }
        
    #     else:
    #          return {"result": False, "err_desc": "Unknown Command", "err_code": 3}

    # except Exception as e:
    #     logger.error(f"❌ Callback Crash: {e}")
    #     import traceback
    #     traceback.print_exc()
    #     return {"result": False, "err_desc": "Internal Error", "err_code": 500}