from typing import List, Optional
from datetime import datetime
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models.player import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerInDB, PlayerStatus
from app.core.security import hash_password
from app.core.permissions import check_permission
from app.dependencies import get_current_admin
from app.schemas.common import ResponseModel

router = APIRouter()

@router.get("", response_model=ResponseModel)
async def list_players(
    page: int = Query(1, gt=0),
    page_size: int = Query(20, gt=0, le=100),
    status: Optional[PlayerStatus] = None,
    search: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    List players with pagination and filtering.
    Requires 'user:read' permission.
    """
    if not await check_permission(current_admin, "user:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    skip = (page - 1) * page_size
    query = {}
    
    if status:
        query["status"] = status.value
    
    if search:
        query["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"player_id": {"$regex": search, "$options": "i"}}
        ]
        
    total = await db.players.count_documents(query)
    cursor = db.players.find(query).skip(skip).limit(page_size).sort("created_at", -1)
    players = await cursor.to_list(length=page_size)
    
    return {
        "success": True,
        "data": [PlayerResponse(**p).model_dump(mode='json') for p in players],
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }

@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_player(
    player_in: PlayerCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Create a new player.
    Requires 'user:write' permission.
    """
    if not await check_permission(current_admin, "user:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Check if exists
        if await db.players.find_one({"username": player_in.username}):
            raise HTTPException(status_code=400, detail="Username already exists")
        
        if player_in.email and await db.players.find_one({"email": player_in.email}):
            raise HTTPException(status_code=400, detail="Email already exists")
            
        player_id = f"user_{secrets.token_hex(8)}"
        
        new_player = PlayerInDB(
            player_id=player_id,
            **player_in.model_dump(exclude={"password"}),
            password_hash=hash_password(player_in.password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await db.players.insert_one(new_player.model_dump())
        return {
            "success": True,
            "data": PlayerResponse(**new_player.model_dump()).model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

@router.get("/{player_id}", response_model=ResponseModel)
async def get_player(
    player_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Get player by ID.
    Requires 'user:read' permission.
    """
    if not await check_permission(current_admin, "user:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    player = await db.players.find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    return {
        "success": True,
        "data": PlayerResponse(**player).model_dump(mode='json')
    }

@router.patch("/{player_id}", response_model=ResponseModel)
async def update_player(
    player_id: str,
    player_update: PlayerUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Update player details.
    Requires 'user:write' permission.
    """
    if not await check_permission(current_admin, "user:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    player = await db.players.find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    update_data = player_update.model_dump(exclude_unset=True)
    if not update_data:
        return ResponseModel(
            success=True,
            data=PlayerResponse(**player)
        )
        
    update_data["updated_at"] = datetime.utcnow()
    
    await db.players.update_one(
        {"player_id": player_id},
        {"$set": update_data}
    )
    
    updated_player = await db.players.find_one({"player_id": player_id})
    return {
        "success": True,
        "data": PlayerResponse(**updated_player).model_dump(mode='json')
    }
