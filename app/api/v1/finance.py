from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import secrets
from typing import List, Optional

from app.database import get_database
from app.dependencies import get_current_admin
from app.core.permissions import check_permission
from app.schemas.common import ResponseModel
from app.models.transaction import (
    TransactionInDB, 
    TransactionResponse, 
    BalanceAdjustmentRequest,
    TransactionType,
    TransactionStatus
)
from app.models.player import PlayerResponse

router = APIRouter()

@router.get("/transactions", response_model=ResponseModel)
async def list_transactions(
    player_id: Optional[str] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """List financial transactions with filters."""
    if not await check_permission(current_admin, "finance:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = {}
    if player_id:
        query["player_id"] = player_id
    if type:
        query["type"] = type.value
        
    skip = (page - 1) * page_size
    total = await db.transactions.count_documents(query)
    cursor = db.transactions.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    transactions = await cursor.to_list(length=page_size)
    
    return {
        "success": True,
        "data": [TransactionResponse(**t).model_dump(mode='json') for t in transactions],
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }

@router.post("/adjust", response_model=ResponseModel)
async def adjust_balance(
    request: BalanceAdjustmentRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Manually adjust a player's balance.
    Creates a transaction log with 'pending' status.
    Balance is ONLY updated after approval.
    """
    if not await check_permission(current_admin, "finance:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # 1. Get current player
    player = await db.players.find_one({"player_id": request.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    amount_before = player.get("balance", 0.0)
    amount_after = amount_before + request.amount
    
    if amount_after < 0:
        raise HTTPException(status_code=400, detail="Insufficient balance for adjustment")
    
    # 2. Create PENDING transaction log
    transaction_id = f"tx_{secrets.token_hex(8)}"
    new_transaction = TransactionInDB(
        transaction_id=transaction_id,
        player_id=request.player_id,
        amount=request.amount,
        type=request.type,
        status=TransactionStatus.PENDING,
        amount_before=amount_before,
        amount_after=amount_after,
        remarks=request.remarks,
        created_by=getattr(current_admin, "admin_id", "system"),
        created_at=datetime.utcnow()
    )
    
    await db.transactions.insert_one(new_transaction.model_dump())
    
    return {
        "success": True,
        "data": TransactionResponse(**new_transaction.model_dump()).model_dump(mode='json')
    }

@router.get("/approvals/pending", response_model=ResponseModel)
async def list_pending_approvals(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """List transactions awaiting approval."""
    if not await check_permission(current_admin, "finance:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    cursor = db.transactions.find({"status": TransactionStatus.PENDING}).sort("created_at", -1)
    pending = await cursor.to_list(length=100)
    
    return {
        "success": True,
        "data": [TransactionResponse(**p).model_dump(mode='json') for p in pending]
    }

@router.post("/approvals/{transaction_id}/approve", response_model=ResponseModel)
async def approve_transaction(
    transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Approve a pending transaction and update player balance."""
    if not await check_permission(current_admin, "finance:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # 1. Get transaction
    tx_doc = await db.transactions.find_one({"transaction_id": transaction_id})
    if not tx_doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    tx = TransactionInDB(**tx_doc)
    
    if tx.status != TransactionStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Transaction is already {tx.status}")
    
    # 2. Dual approval check: Creator cannot be Approver
    approver_id = getattr(current_admin, "admin_id", "system")
    if tx.created_by == approver_id:
        # For testing purposes, we might want to bypass this if it's the only admin
        # but the requirement says "Dual Confirmation".
        raise HTTPException(status_code=400, detail="Creator cannot approve their own transaction")
    
    # 3. Apply balance change to player
    # Atomic update
    update_result = await db.players.update_one(
        {"player_id": tx.player_id},
        {"$inc": {"balance": tx.amount}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update player balance")
        
    # 4. Update transaction status
    await db.transactions.update_one(
        {"transaction_id": transaction_id},
        {
            "$set": {
                "status": TransactionStatus.COMPLETED,
                "approved_by": approver_id,
                "approved_at": datetime.utcnow()
            }
        }
    )
    
    return {"success": True, "data": {"message": "Transaction approved"}}

@router.post("/approvals/{transaction_id}/reject", response_model=ResponseModel)
async def reject_transaction(
    transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Reject a pending transaction."""
    if not await check_permission(current_admin, "finance:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
        
    # 1. Get transaction
    tx_doc = await db.transactions.find_one({"transaction_id": transaction_id})
    if not tx_doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    if tx_doc["status"] != TransactionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending transactions can be rejected")

    await db.transactions.update_one(
        {"transaction_id": transaction_id},
        {"$set": {"status": TransactionStatus.FAILED}}
    )
    
    return {"success": True, "data": {"message": "Transaction rejected"}}

@router.post("/withdrawals/request", response_model=ResponseModel)
async def request_withdrawal(
    request: BalanceAdjustmentRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Create a pending withdrawal request."""
    if not await check_permission(current_admin, "finance:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Withdrawal amount should be negative
    amount = request.amount if request.amount < 0 else -request.amount
        
    player = await db.players.find_one({"player_id": request.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    amount_before = player.get("balance", 0.0)
    amount_after = amount_before + amount
    
    if amount_after < 0:
        raise HTTPException(status_code=400, detail="Insufficient balance for withdrawal")
        
    transaction_id = f"tx_{secrets.token_hex(8)}"
    new_transaction = TransactionInDB(
        transaction_id=transaction_id,
        player_id=request.player_id,
        amount=amount,
        type=TransactionType.WITHDRAWAL,
        status=TransactionStatus.PENDING,
        amount_before=amount_before,
        amount_after=amount_after,
        remarks=request.remarks,
        created_by=getattr(current_admin, "admin_id", "system"),
        created_at=datetime.utcnow()
    )
    
    await db.transactions.insert_one(new_transaction.model_dump())
    
    return {
        "success": True,
        "data": TransactionResponse(**new_transaction.model_dump()).model_dump(mode='json')
    }
