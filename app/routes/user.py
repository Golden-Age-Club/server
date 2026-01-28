from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from app.repositories.user import UserRepository
from app.dependencies import get_user_repo
from app.schemas.user import UserResponse
import logging

router = APIRouter(prefix="/api/users", tags=["users"])
logger = logging.getLogger(__name__)

@router.get("/top-users", response_model=List[UserResponse])
async def get_top_users(
    limit: int = Query(100, ge=1, le=100),
    user_repo: UserRepository = Depends(get_user_repo)
):
    """Get top users sorted by total winnings"""
    users = await user_repo.get_top_users(limit)
    
    # Convert _id to string for Pydantic compatibility
    for user in users:
        if "_id" in user:
            user["_id"] = str(user["_id"])
            
    return users
