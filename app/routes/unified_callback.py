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
from app.dependencies import get_user_repo
from app.middleware.auth import verify_access_token

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
async def unified_callbackw(request: Request, user_repo: UserRepository = Depends(get_user_repo)):
    try:
        body = await request.json()
        print(body)
        cmd = body.get('cmd')
        player_token = body.get('player_token')
    

        # 1. FLEXIBLE TOKEN DECODING
        user_id = None
        try:
            # Try your JWT logic first
            payload = verify_access_token(player_token)
            # Support both 'user_id' (from user input) and 'sub' (standard JWT)
            user_id = payload.get("user_id") or payload.get("sub")
        except Exception:
            # If JWT fails, try Base64 (like the MGC sample)
            try:
                decoded = base64.b64decode(player_token).decode('utf-8')
                user_id = json.loads(decoded).get('player_id')
            except:
                logger.error("Could not decode player_token via JWT or Base64")

        if not user_id:
            return {"result": False, "err_desc": "Player Not Found", "err_code": 2}

        user = await user_repo.get_by_id(user_id)
        if not user:
            return {"result": False, "err_desc": "Player Not Found", "err_code": 2}

        # 2. HANDLE COMMANDS
        if cmd == 'getPlayerInfo' or cmd == 'getBalance':
            print({  "result": True,
                "err_desc": "OK",
                "err_code": 0,
                "currency": "USD",
                "balance": float(user.get("balance", 0)),
                "display_name": user.get("username", "Player"),
                "gender": "m",
                "country": "US",
                "player_id": str(user["_id"])})
            return {
                "result": True,
                "err_desc": "OK",
                "err_code": 0,
                "currency": "USD",
                "balance": float(user.get("balance", 0)),
                "display_name": user.get("username", "Player"),
                "gender": "m",
                "country": "US",
                "player_id": str(user["_id"])
            }

        elif cmd == 'deposit':
            # "deposit" usually means the player WON (money comes IN to the wallet)
            # Log shows: 'winAmount': 0 (or >0 if win), 'betInfo': '...'
            amount = float(body.get('winAmount', 0))
            
            before_balance = float(user.get("balance", 0))
            new_balance = await user_repo.update_balance(str(user["_id"]), amount)
            
            # Use provided transactionId or generate one
            tx_id = body.get('transactionId') or f"dep_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}"
            
            return {
                "result": True,
                "err_desc": "OK",
                "err_code": 0,
                "balance": new_balance,
                "before_balance": before_balance,
                "transactionId": tx_id
            }

        elif cmd == 'withdraw':
            # "withdraw" usually means the player BET (money goes OUT of the wallet)
            # Log shows: 'betAmount': 100
            amount = float(body.get('betAmount', 0))
            
            before_balance = float(user.get("balance", 0))
            try:
                new_balance = await user_repo.deduct_balance(str(user["_id"]), amount)
            except HTTPException:
                return {"result": False, "err_desc": "Insufficient balance", "err_code": 100}
                
            tx_id = body.get('transactionId') or f"wd_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}"
            
            return {
                "result": True,
                "err_desc": "OK",
                "err_code": 0,
                "balance": new_balance,
                "before_balance": before_balance,
                "transactionId": tx_id
            }

        elif cmd == 'rollback':
            # Rollback: Refund a previous transaction (usually a bet/withdraw)
            # Log shows: 'transactionId', but amount might not be explicit in simple rollback
            # However, typically rollback includes the amount to refund or we might need to look it up.
            # Based on logs provided, rollback doesn't show amount, but let's check standard PG/MGC logic.
            # Usually rollback provides 'betAmount' or 'amount' to refund.
            # If not present, we might need to assume it's full refund or handle 0 safely.
            # Let's check if 'betAmount' or 'amount' is in body for rollback.
            # If strictly following logs: {'cmd': 'rollback', ...} no amount shown in your snippet.
            # But normally rollback cancels a bet, so we should ADD back the money.
            
            # SAFELY GET AMOUNT:
            amount = float(body.get('betAmount', 0)) # Try betAmount first (common in bet cancellations)
            if amount == 0:
                 amount = float(body.get('amount', 0)) # Fallback generic amount
            
            before_balance = float(user.get("balance", 0))
            new_balance = await user_repo.update_balance(str(user["_id"]), amount)
            
            tx_id = body.get('transactionId') or f"rb_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}"
            
            return {
                "result": True,
                "err_desc": "OK",
                "err_code": 0,
                "balance": new_balance,
                "before_balance": before_balance,
                "transactionId": tx_id
            }

        # 3. ACKNOWLEDGE OTHERS
        elif cmd in ['bet', 'win', 'refund']:
            # Fallback for other commands if any
            return {
                "result": True,
                "err_desc": "OK",
                "err_code": 0,
                "balance": float(user.get("balance", 0))
            }

    except Exception as e:
        logger.error(f"❌ Callback Crash: {e}")
        return {"result": False, "err_desc": "Internal Error", "err_code": 500}