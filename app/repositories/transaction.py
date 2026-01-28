from datetime import datetime
from typing import Optional, Dict, List
from bson import ObjectId
from app.core.database import get_database
from app.models.transaction import TransactionStatus, TransactionType

class TransactionRepository:
    def __init__(self, db):
        self.db = db
        self.collection = db.transactions
    
    async def create(
        self,
        user_id: str,
        transaction_type: TransactionType,
        amount: float,
        currency: str,
        status: TransactionStatus = TransactionStatus.PENDING,
        **kwargs
    ) -> str:
        transaction = {
            "user_id": user_id,
            "type": transaction_type,
            "amount": amount,
            "currency": currency,
            "status": status,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }
        
        result = await self.collection.insert_one(transaction)
        return str(result.inserted_id)
    
    async def get_by_id(self, transaction_id: str) -> Optional[Dict]:
        transaction = await self.collection.find_one({"_id": ObjectId(transaction_id)})
        if transaction:
            transaction["_id"] = str(transaction["_id"])
        return transaction
    
    async def get_by_merchant_order_id(self, merchant_order_id: str) -> Optional[Dict]:
        transaction = await self.collection.find_one({"merchant_order_id": merchant_order_id})
        if transaction:
            transaction["_id"] = str(transaction["_id"])
        return transaction
    
    async def update_status(
        self,
        transaction_id: str,
        status: TransactionStatus,
        **kwargs
    ):
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow(),
            **kwargs
        }
        
        await self.collection.update_one(
            {"_id": ObjectId(transaction_id)},
            {"$set": update_data}
        )
    
    async def get_user_transactions(self, user_id: str, limit: int = 50) -> List[Dict]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        transactions = await cursor.to_list(length=limit)
        
        for t in transactions:
            t["_id"] = str(t["_id"])
        
        return transactions

    async def get_recent_transactions(self, limit: int = 50) -> List[Dict]:
        cursor = self.collection.find().sort("created_at", -1).limit(limit)
        transactions = await cursor.to_list(length=limit)
        
        for t in transactions:
            t["_id"] = str(t["_id"])
        
        return transactions