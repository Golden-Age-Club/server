from datetime import datetime
from typing import Optional
from app.core.database import get_database
from fastapi import HTTPException

class UserRepository:
    def __init__(self, db):
        self.db = db
        self.collection = db.users
    
    async def create_user(self, user_data: dict) -> str:
        """Create a new user and return telegram_id"""
        user_doc = {
            "_id": user_data["telegram_id"],  # Use telegram_id as primary key
            "telegram_id": user_data["telegram_id"],
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "photo_url": user_data.get("photo_url"),
            "language_code": user_data.get("language_code", "en"),
            "balance": 0.0,
            "is_active": True,
            "is_premium": user_data.get("is_premium", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.collection.insert_one(user_doc)
        return str(user_data["telegram_id"])
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """Get user by Telegram ID"""
        user = await self.collection.find_one({"_id": telegram_id})
        return user
    
    async def update_user_info(self, telegram_id: int, user_data: dict) -> None:
        """Update user information"""
        update_data = {
            **user_data,
            "updated_at": datetime.utcnow()
        }
        
        await self.collection.update_one(
            {"_id": telegram_id},
            {"$set": update_data}
        )
    
    async def get_balance(self, user_id: str) -> float:
        """Get user's current balance. Raises error if user doesn't exist."""
        # Support both string user_id and telegram_id lookup
        try:
            telegram_id = int(user_id)
            user = await self.collection.find_one({"_id": telegram_id})
        except ValueError:
            user = await self.collection.find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.get("balance", 0.0)
    
    async def get_balance_or_default(self, user_id: str) -> float:
        """Get user's balance or return 0.0 if user doesn't exist."""
        try:
            telegram_id = int(user_id)
            user = await self.collection.find_one({"_id": telegram_id})
        except ValueError:
            user = await self.collection.find_one({"_id": user_id})
        
        return user.get("balance", 0.0) if user else 0.0
    
    async def update_balance(self, user_id: str, amount: float) -> float:
        """Atomically update balance and return new balance. Raises error if user doesn't exist."""
        # Support both string user_id and telegram_id lookup
        try:
            telegram_id = int(user_id)
            query = {"_id": telegram_id}
        except ValueError:
            query = {"_id": user_id}
        
        # First ensure user exists
        user = await self.collection.find_one(query)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Atomic update with return of new value
        result = await self.collection.find_one_and_update(
            query,
            {
                "$inc": {"balance": amount},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        return result.get("balance", 0.0)
    
    async def deduct_balance(self, user_id: str, amount: float) -> float:
        """Atomically deduct amount from balance, checking it doesn't go negative."""
        # Support both string user_id and telegram_id lookup
        try:
            telegram_id = int(user_id)
            query = {"_id": telegram_id}
        except ValueError:
            query = {"_id": user_id}
        
        user = await self.collection.find_one(query)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_balance = user.get("balance", 0.0)
        if current_balance < amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available: {current_balance} USDT, Required: {amount} USDT"
            )
        
        result = await self.collection.find_one_and_update(
            {**query, "balance": {"$gte": amount}},
            {
                "$inc": {"balance": -amount},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        if result is None:
            raise HTTPException(status_code=400, detail="Balance changed during transaction")
        
        return result.get("balance", 0.0)
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by user_id (supports both telegram_id and string id)"""
        try:
            telegram_id = int(user_id)
            return await self.collection.find_one({"_id": telegram_id})
        except ValueError:
            return await self.collection.find_one({"_id": user_id})
