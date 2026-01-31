from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List

from app.database import get_database
from app.dependencies import get_current_admin
from app.core.permissions import check_permission
from app.schemas.common import ResponseModel
from app.models.vip import VIPTierConfig, VIPConfigRequest, VIPLevelAdjustmentRequest
from app.models.player import PlayerResponse

router = APIRouter()

@router.get("/configs", response_model=ResponseModel)
async def get_vip_configs(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Get all VIP tier configurations."""
    if not await check_permission(current_admin, "vip:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    configs = await db.vip_configs.find().sort("level", 1).to_list(length=20)
    
    # If no configs yet, return defaults
    if not configs:
        configs = [
            {"level": 0, "name": "Bronze", "min_deposits": 0, "min_bet_amount": 0, "benefits": ["Standard support"]},
            {"level": 1, "name": "Silver", "min_deposits": 1000, "min_bet_amount": 10000, "benefits": ["Priority support", "Weekly bonus"]},
            {"level": 2, "name": "Gold", "min_deposits": 5000, "min_bet_amount": 50000, "benefits": ["Dedicated manager", "Daily bonus", "Higher limits"]},
            {"level": 3, "name": "Platinum", "min_deposits": 20000, "min_bet_amount": 200000, "benefits": ["Exclusive events", "Instant withdrawals", "Custom bonuses"]}
        ]
        # Seed them in DB
        await db.vip_configs.insert_many(configs)
    
    # Remove _id for serialization
    for c in configs:
        if "_id" in c:
            del c["_id"]
    
    return {
        "success": True,
        "data": configs
    }

@router.put("/configs", response_model=ResponseModel)
async def update_vip_configs(
    request: VIPConfigRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Update VIP tier configurations."""
    if not await check_permission(current_admin, "vip:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Replace all configs
    await db.vip_configs.delete_many({})
    await db.vip_configs.insert_many([t.model_dump() for t in request.tiers])
    
    return {"success": True, "data": {"message": "VIP configurations updated"}}

@router.get("/high-value", response_model=ResponseModel)
async def get_high_value_players(
    min_level: int = 1,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Get high-value players based on VIP level or total deposits."""
    if not await check_permission(current_admin, "vip:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Query for players with high VIP level or high deposits
    query = {
        "$or": [
            {"vip_level": {"$gte": min_level}},
            {"total_deposits": {"$gte": 5000}}
        ]
    }
    
    cursor = db.players.find(query).sort("vip_level", -1).limit(50)
    players = await cursor.to_list(length=50)
    
    return {
        "success": True,
        "data": [PlayerResponse(**p).model_dump(mode='json') for p in players]
    }

@router.post("/adjust-level", response_model=ResponseModel)
async def adjust_player_vip(
    request: VIPLevelAdjustmentRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Manually adjust a player's VIP level."""
    if not await check_permission(current_admin, "vip:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update player
    update_result = await db.players.update_one(
        {"player_id": request.player_id},
        {"$set": {"vip_level": request.new_level, "updated_at": datetime.utcnow()}}
    )
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Player not found")
        
    return {"success": True, "data": {"message": f"VIP level updated to {request.new_level}"}}
