from datetime import datetime
from typing import Optional
from app.core.database import get_database
from fastapi import HTTPException

class UserRepository:
    def __init__(self, db):
        self.db = db
        self.collection = db.users
    
    async def create_user(self, user_data: dict) -> str:
        """Create a new user (Telegram)"""
        # Generate new ObjectId automatically by not specifying _id, or use provided one
        user_doc = {
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
        
        result = await self.collection.insert_one(user_doc)
        return str(result.inserted_id)

    async def create_email_user(self, user_data: dict) -> str:
        """Create a new user (Email)"""
        user_doc = {
            "email": user_data["email"],
            "username": user_data["username"],
            "password_hash": user_data["password_hash"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "language_code": "en",
            "balance": 0.0,
            "is_active": True,
            "is_premium": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(user_doc)
        return str(result.inserted_id)
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """Get user by Telegram ID"""
        # Telegram ID is no longer _id, it's a field
        user = await self.collection.find_one({"telegram_id": telegram_id})
        return user

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Get user by Email"""
        user = await self.collection.find_one({"email": email})
        return user

    async def get_by_username(self, username: str) -> Optional[dict]:
        """Get user by Username"""
        user = await self.collection.find_one({"username": username})
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by database ID"""
        try:
             from bson import ObjectId
             oid = ObjectId(user_id)
             return await self.collection.find_one({"_id": oid})
        except:
             return None

    async def update_user_info(self, telegram_id: int, user_data: dict) -> None:
        """Update user information by telegram_id"""
        update_data = {
            **user_data,
            "updated_at": datetime.utcnow()
        }
        
        await self.collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": update_data}
        )
    
    async def get_balance(self, user_id: str) -> float:
        """Get user's current balance."""
        user = await self.get_by_id(user_id)
        
        # Fallback for legacy (if any) or mixed usage, try finding by telegram_id?
        # Ideally we stick to ID. But the system might pass telegram_id string.
        if not user and user_id.isdigit():
             user = await self.get_by_telegram_id(int(user_id))
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.get("balance", 0.0)
    
    async def get_balance_or_default(self, user_id: str) -> float:
        """Get user's balance or return 0.0 if user doesn't exist."""
        try:
            return await self.get_balance(user_id)
        except HTTPException:
            return 0.0
    
    async def update_balance(self, user_id: str, amount: float) -> float:
        """Atomically update balance."""
        from bson import ObjectId
        query = {}
        try:
            query = {"_id": ObjectId(user_id)}
        except:
            if user_id.isdigit():
                query = {"telegram_id": int(user_id)}
            else:
                raise HTTPException(status_code=404, detail="Invalid ID format")
        
        # First ensure user exists
        user = await self.collection.find_one(query)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
        """Atomically deduct amount."""
        from bson import ObjectId
        query = {}
        try:
            query = {"_id": ObjectId(user_id)}
        except:
            if user_id.isdigit():
                query = {"telegram_id": int(user_id)}
            else:
                raise HTTPException(status_code=404, detail="Invalid ID format")
        
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
        """Get user by user_id"""
        return await self.get_by_id(user_id)
