from typing import List, Optional
from datetime import datetime
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models.game import GameCreate, GameUpdate, GameResponse, GameInDB, GameStatus
from app.core.permissions import check_permission
from app.dependencies import get_current_admin
from app.schemas.common import ResponseModel

router = APIRouter()

@router.get("", response_model=ResponseModel)
async def list_games(
    page: int = Query(1, gt=0),
    page_size: int = Query(20, gt=0, le=100),
    status: Optional[GameStatus] = None,
    provider: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    List games with pagination and filtering.
    Requires 'game:read' permission.
    """
    if not await check_permission(current_admin, "game:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    skip = (page - 1) * page_size
    query = {}
    
    if status:
        query["status"] = status.value
    
    if provider:
        query["provider"] = provider
        
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"provider": {"$regex": search, "$options": "i"}}
        ]
        
    total = await db.games.count_documents(query)
    cursor = db.games.find(query).skip(skip).limit(page_size).sort("created_at", -1)
    games = await cursor.to_list(length=page_size)
    
    return {
        "success": True,
        "data": [GameResponse(**g).model_dump(mode='json') for g in games],
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }

@router.post("", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_in: GameCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Create a new game.
    Requires 'game:write' permission.
    """
    if not await check_permission(current_admin, "game:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if exists (by name and provider)
    if await db.games.find_one({"name": game_in.name, "provider": game_in.provider}):
        raise HTTPException(status_code=400, detail="Game already exists")
    
    game_id = f"game_{secrets.token_hex(8)}"
    
    new_game = GameInDB(
        game_id=game_id,
        **game_in.model_dump(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    await db.games.insert_one(new_game.model_dump())
    return {
        "success": True,
        "data": GameResponse(**new_game.model_dump()).model_dump(mode='json')
    }

@router.get("/{game_id}", response_model=ResponseModel)
async def get_game(
    game_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Get game by ID.
    Requires 'game:read' permission.
    """
    if not await check_permission(current_admin, "game:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    game = await db.games.find_one({"game_id": game_id})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
        
    return {
        "success": True,
        "data": GameResponse(**game).model_dump(mode='json')
    }

@router.patch("/{game_id}", response_model=ResponseModel)
async def update_game(
    game_id: str,
    game_update: GameUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Update game details.
    Requires 'game:write' permission.
    """
    if not await check_permission(current_admin, "game:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    game = await db.games.find_one({"game_id": game_id})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    update_data = game_update.model_dump(exclude_unset=True)
    if not update_data:
        return ResponseModel(
            success=True,
            data=GameResponse(**game)
        )
        
    update_data["updated_at"] = datetime.utcnow()
    
    await db.games.update_one(
        {"game_id": game_id},
        {"$set": update_data}
    )
    
    updated_game = await db.games.find_one({"game_id": game_id})
    return {
        "success": True,
        "data": GameResponse(**updated_game).model_dump(mode='json')
    }

@router.delete("/{game_id}", response_model=ResponseModel)
async def delete_game(
    game_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """
    Delete a game.
    Requires 'game:write' permission.
    """
    if not await check_permission(current_admin, "game:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await db.games.delete_one({"game_id": game_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Game not found")

    return {
        "success": True,
        "data": {"message": "Game deleted successfully"}
    }
    """
    Delete a game.
    Requires 'game:write' permission.
    """
    if not await check_permission(current_admin, "game:write", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await db.games.delete_one({"game_id": game_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Game not found")
