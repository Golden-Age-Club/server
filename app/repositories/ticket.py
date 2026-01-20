"""
Minimal Ticket Repository
"""
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from app.core.database import get_database
from app.models.ticket import TicketStatus


class TicketRepository:
    def __init__(self, db):
        self.collection = db.tickets

    async def create(self, user_id: str) -> str:
        """Create a new open ticket"""
        doc = {
            "user_id": user_id,
            "status": TicketStatus.OPEN,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_by_id(self, ticket_id: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(ticket_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except:
            return None

    async def get_user_tickets(self, user_id: str) -> List[dict]:
        """Get all tickets for a user, sorted by updated_at desc"""
        cursor = self.collection.find({"user_id": user_id}).sort("updated_at", -1)
        docs = await cursor.to_list(None)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    async def get_all_open(self) -> List[dict]:
        """Get all open tickets for admin"""
        cursor = self.collection.find({"status": TicketStatus.OPEN}).sort("updated_at", -1)
        docs = await cursor.to_list(None)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
        
    async def resolve(self, ticket_id: str) -> bool:
        """Mark ticket as resolved"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(ticket_id)},
                {"$set": {
                    "status": TicketStatus.RESOLVED,
                    "updated_at": datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except:
            return False

    async def touch(self, ticket_id: str):
        """Update updated_at timestamp (when new message arrives)"""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(ticket_id)},
                {"$set": {"updated_at": datetime.utcnow()}}
            )
        except:
            pass
