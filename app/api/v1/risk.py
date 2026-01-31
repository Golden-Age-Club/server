from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime

from app.database import get_database
from app.dependencies import get_current_admin
from app.core.permissions import check_permission
from app.schemas.common import ResponseModel
from app.models.risk import RiskRule, RiskAlert

router = APIRouter()

@router.get("/rules", response_model=ResponseModel)
async def get_risk_rules(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Get all risk control rules."""
    if not await check_permission(current_admin, "risk:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    rules = await db.risk_rules.find().to_list(length=100)
    
    # Seed default rules if empty
    if not rules:
        rules = [
            {
                "rule_id": "rule_1",
                "type": "withdrawal_freq",
                "threshold": 5.0,
                "time_window_minutes": 60,
                "action": "review",
                "is_active": True,
                "description": "More than 5 withdrawals in 1 hour"
            },
            {
                "rule_id": "rule_2",
                "type": "large_bet",
                "threshold": 1000.0,
                "action": "flag",
                "is_active": True,
                "description": "Single bet greater than $1000"
            }
        ]
        await db.risk_rules.insert_many(rules)
    
    # Clean _id
    for r in rules:
        if "_id" in r: del r["_id"]
        
    return {"success": True, "data": rules}

@router.get("/alerts", response_model=ResponseModel)
async def get_risk_alerts(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Get active risk alerts."""
    if not await check_permission(current_admin, "risk:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    alerts = await db.risk_alerts.find().sort("created_at", -1).to_list(length=100)
    for a in alerts:
        if "_id" in a: del a["_id"]
        
    return {"success": True, "data": alerts}
