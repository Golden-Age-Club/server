from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime
import uuid

from app.database import get_database
from app.dependencies import get_current_admin
from app.core.permissions import check_permission
from app.schemas.common import ResponseModel
from app.models.promotion import Promotion, PromotionStatus

router = APIRouter()

@router.get("/", response_model=ResponseModel)
async def get_promotions(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Get all promotions."""
    if not await check_permission(current_admin, "promotions:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    promos = await db.promotions.find().sort("created_at", -1).to_list(length=100)
    for p in promos:
        if "_id" in p: del p["_id"]
        
    return {"success": True, "data": promos}

@router.post("/", response_model=ResponseModel)
async def create_promotion(
    promo: Promotion,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """Create a new promotion."""
    if not await check_permission(current_admin, "promotions:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    promo_data = promo.model_dump()
    await db.promotions.insert_one(promo_data)
    
    if "_id" in promo_data: del promo_data["_id"]
    return {"success": True, "data": promo_data}
