from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import json
import base64
from datetime import datetime
from app.repositories.user import UserRepository
from app.repositories.transaction import TransactionRepository
from app.dependencies import get_user_repo, get_transaction_repo
from app.models.transaction import TransactionType, TransactionStatus
from app.middleware.auth import verify_access_token

router = APIRouter(tags=["callback"])
logger = logging.getLogger(__name__)

@router.post("/api/callback")
async def unified_callback(
    request: Request, 
    user_repo: UserRepository = Depends(get_user_repo),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo)
):
    try:
        data = await request.json()
        logger.info(f"Callback Received: {data}")

        cmd = data.get('cmd')
        player_token = data.get('player_token')
        transaction_id = data.get('transactionId')
        round_id = data.get('roundId')
        game_id = data.get('gameId')
        currency_id = data.get('currencyId')
        bet_amount = float(data.get('betAmount', 0))
        win_amount = float(data.get('winAmount', 0))
        amount = float(data.get('amount', 0)) # Generic amount
        bet_info = data.get('betInfo')
        request_time = data.get('request_time')
        signature = data.get('signature')

        # 1. Decode Player Token
        user_id = None
        try:
            # Try JWT first (as per previous context)
            payload = verify_access_token(player_token)
            user_id = payload.get("user_id") or payload.get("sub")
        except:
            try:
                # Try Base64 JSON (as per sample)
                decoded = base64.b64decode(player_token).decode('utf-8')
                if decoded.startswith('{'):
                    decoded_json = json.loads(decoded)
                    user_id = decoded_json.get('player_id') or decoded_json.get('user_id')
                else:
                    user_id = decoded
            except Exception as e:
                logger.error(f"Token decode failed: {e}")
                return {
                    'result': True,
                    'err_desc': 'Invalid token',
                    'err_code': 401
                }

        if not user_id:
             return {
                'result': True,
                'err_desc': 'Player not found',
                'err_code': 2
            }

        # 2. Get User & Balance
        user = await user_repo.get_by_id(user_id)
        if not user and str(user_id).isdigit():
             user = await user_repo.get_by_telegram_id(int(user_id))
        
        if not user:
            return {
                'result': True,
                'err_desc': 'Player not found',
                'err_code': 2
            }

        user_id_str = str(user["_id"])
        # Ensure currency matches if needed, or default to user's currency
        # Sample uses currency_id from request. 

        # 3. Handle Commands
        
        # WITHDRAW
        if cmd == 'withdraw':
            # Check for existing transaction
            existing_tx = await transaction_repo.get_by_merchant_order_id(transaction_id)
            if existing_tx:
                return {
                    'result': False, # Success (Idempotent)
                    'err_desc': 'Transaction already processed',
                    'err_code': 0,
                    'balance': float(user.get("balance", 0)),
                    'before_balance': float(user.get("balance", 0)), # Approx
                    'transactionId': transaction_id
                }

            before_balance = float(user.get("balance", 0))
            new_balance = before_balance - bet_amount

            # Insufficient Balance
            if new_balance < 0:
                return {
                    'result': True, # Error
                    'err_desc': 'Insufficient balance',
                    'err_code': 3,
                    'balance': before_balance,
                    'before_balance': before_balance,
                    'transactionId': transaction_id
                }

            # Execute Transaction
            await user_repo.update_balance(user_id_str, -bet_amount) # Deduct
            await user_repo.update_game_stats(user_id_str, bet_amount=bet_amount)

            await transaction_repo.create(
                user_id=user_id_str,
                transaction_type=TransactionType.GAME_BET,
                amount=bet_amount,
                currency=currency_id or "USD",
                status=TransactionStatus.COMPLETED,
                merchant_order_id=transaction_id,
                game_id=game_id,
                round_id=round_id,
                bet_info=bet_info
            )

            return {
                'result': False, # Success
                'err_desc': 'OK',
                'err_code': 0,
                'balance': new_balance,
                'before_balance': before_balance,
                'transactionId': transaction_id
            }

        # DEPOSIT
        elif cmd == 'deposit':
            # Check for existing transaction
            existing_tx = await transaction_repo.get_by_merchant_order_id(transaction_id)
            if existing_tx:
                return {
                    'result': False,
                    'err_desc': 'Transaction already processed',
                    'err_code': 0,
                    'balance': float(user.get("balance", 0)),
                    'before_balance': float(user.get("balance", 0)),
                    'transactionId': transaction_id
                }

            before_balance = float(user.get("balance", 0))
            new_balance = before_balance + win_amount

            # Execute Transaction
            await user_repo.update_balance(user_id_str, win_amount) # Add
            await user_repo.update_game_stats(user_id_str, win_amount=win_amount)

            await transaction_repo.create(
                user_id=user_id_str,
                transaction_type=TransactionType.GAME_WIN,
                amount=win_amount,
                currency=currency_id or "USD",
                status=TransactionStatus.COMPLETED,
                merchant_order_id=transaction_id,
                game_id=game_id,
                round_id=round_id,
                bet_info=bet_info
            )

            return {
                'result': False,
                'err_desc': 'OK',
                'err_code': 0,
                'balance': new_balance,
                'before_balance': before_balance,
                'transactionId': transaction_id
            }

        # ROLLBACK
        elif cmd == 'rollback':
            # 1. Check if the original transaction exists (the one to be rolled back)
            original_tx = await transaction_repo.get_by_merchant_order_id(transaction_id)
            if not original_tx:
                 # Sample says: return Error 2 "Transaction not found"
                 # BUT, if it's not found, maybe we should just ignore it?
                 # Sample code returns 404.
                 return {
                    'result': True,
                    'err_desc': 'Transaction not found',
                    'err_code': 2
                }
            
            # 2. Check if ALREADY rolled back
            # We need to find if there is a 'rollback' type transaction with THIS transactionId
            # But wait, usually 'transactionId' in the request IS the ID of the transaction to rollback.
            # And the rollback itself should have a NEW ID?
            # Or does the provider send the SAME transactionId for the rollback command?
            # The sample query: "SELECT transactionId FROM transactions WHERE transactionId = %s AND type = 'rollback'"
            # This implies the provider sends the SAME transactionId for the rollback.
            # AND the original transaction ALSO has that transactionId.
            # So we have TWO transactions with the same 'merchant_order_id' (transactionId)?
            # One is 'withdraw'/'deposit', the other is 'rollback'.
            
            # My repo `get_by_merchant_order_id` returns ONE.
            # I need to check specifically for the rollback type.
            
            # Since my repo might not support complex filtering yet, I'll do a custom find in the route or expand repo.
            # Let's expand repo logic slightly by using the collection directly if needed or assuming strict 1-to-1 mapping isn't enough.
            # Actually, standard Mongo repo usage:
            
            # Check for existing ROLLBACK for this transaction ID
            existing_rollback = await transaction_repo.collection.find_one({
                "merchant_order_id": transaction_id,
                "type": TransactionType.GAME_REFUND # Using REFUND as Rollback
            })
            
            if existing_rollback:
                return {
                    'result': False,
                    'err_desc': 'Rollback already processed',
                    'err_code': 0,
                    'balance': float(user.get("balance", 0)),
                    'before_balance': float(user.get("balance", 0)),
                    'transactionId': transaction_id
                }

            # 3. Process Logic
            transaction_type = original_tx['type']
            transaction_amount = float(original_tx['amount'])
            
            before_balance = float(user.get("balance", 0))
            new_balance = before_balance
            
            if transaction_type == TransactionType.GAME_BET: # withdraw in sample
                # Reverse withdraw -> Add money back
                new_balance = before_balance + transaction_amount
                await user_repo.update_balance(user_id_str, transaction_amount)
                
            elif transaction_type == TransactionType.GAME_WIN: # deposit in sample
                # Reverse deposit -> Deduct money
                new_balance = before_balance - transaction_amount
                if new_balance < 0:
                     return {
                        'result': True,
                        'err_desc': 'Insufficient balance for rollback',
                        'err_code': 4,
                        'balance': before_balance,
                        'before_balance': before_balance,
                        'transactionId': transaction_id
                    }
                await user_repo.update_balance(user_id_str, -transaction_amount)
            
            else:
                 return {
                    'result': True,
                    'err_desc': 'Invalid transaction type for rollback',
                    'err_code': 5
                }
            
            # 4. Record the Rollback
            await transaction_repo.create(
                user_id=user_id_str,
                transaction_type=TransactionType.GAME_REFUND,
                amount=transaction_amount,
                currency=currency_id or "USD",
                status=TransactionStatus.COMPLETED,
                merchant_order_id=transaction_id, # Same ID as original, distinguished by type
                game_id=game_id,
                round_id=round_id,
                bet_info=bet_info
            )

            return {
                'result': False,
                'err_desc': 'OK',
                'err_code': 0,
                'balance': new_balance,
                'before_balance': before_balance,
                'transactionId': transaction_id
            }

        # GET PLAYER INFO (Required for handshake)
        elif cmd == 'getPlayerInfo' or cmd == 'getBalance':
             currency = currency_id or user.get('currency', 'USD')
             return {
                "result": True,
                "err_desc": "OK",
                "err_code": 0,
                "currency": currency,
                "currencyId": currency,
                "balance": float(user.get("balance", 0)),
                "display_name": user.get("username", "Player"),
                "player_id": user_id_str,
                "partnerPlayerId": user_id_str,
                "vipLevel": 0
            }

        else:
            return {
                'result': True,
                'err_desc': 'Invalid command',
                'err_code': 4
            }

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {
            'result': True,
            'err_desc': 'Internal server error',
            'err_code': 500
        }
