"""
Minimal Support Message Repository
"""
from datetime import datetime
from typing import List
from bson import ObjectId


class SupportMessageRepository:
    def __init__(self, db):
        self.collection = db.support_messages

    async def create(self, ticket_id: str, sender_id: str, role: str, content: str) -> dict:
        """Create and save a new message"""
        doc = {
            "ticket_id": ticket_id,
            "sender_id": sender_id,
            "sender_role": role,
            "content": content,
            "created_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    async def get_history(self, ticket_id: str) -> List[dict]:
        """Get full chat history for a ticket"""
        cursor = self.collection.find({"ticket_id": ticket_id}).sort("created_at", 1)
        docs = await cursor.to_list(None)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
