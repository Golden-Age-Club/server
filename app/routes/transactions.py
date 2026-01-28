from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from app.repositories.transaction import TransactionRepository
from app.dependencies import get_transaction_repo
from app.repositories.user import UserRepository
from app.dependencies import get_user_repo
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.get("/recent")
async def get_recent_transactions(
    limit: int = Query(50, ge=1, le=100),
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
    user_repo: UserRepository = Depends(get_user_repo)
):
    """
    Get recent global transactions for the live feed.
    """
    transactions = await transaction_repo.get_recent_transactions(limit=limit)
    
    # Enrich with usernames if possible, though repository might just have user_id
    # We might need to fetch usernames. 
    # For efficiency, we could aggregate, but for now let's just loop or assume username is not strictly required 
    # OR we can fetch user details.
    
    # Let's try to get usernames for better display
    results = []
    for tx in transactions:
        user_id = tx.get("user_id")
        username = "Player"
        if user_id:
            try:
                user = await user_repo.get_by_id(user_id)
                if user:
                    username = user.get("username", "Player")
            except:
                pass
        
        tx_type = tx.get("type")
        if tx_type == "game_win":
            mapped_type = "win"
        elif tx_type == "game_bet":
            mapped_type = "bet"
        elif tx_type == "game_refund":
            mapped_type = "refund"
        else:
            mapped_type = tx_type

        results.append({
            "transaction_id": tx["_id"],
            "user_id": user_id,
            "username": username,
            "amount": tx.get("amount", 0),
            "currency": tx.get("currency", "USD"),
            "type": mapped_type,
            "game_id": tx.get("game_id", "Unknown Game"),
            "timestamp": tx.get("created_at")
        })
            
    return results
