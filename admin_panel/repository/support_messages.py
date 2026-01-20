from pymongo import MongoClient
import os
from config.settings import DATABASES

class SupportMessageRepository:
    """
    Django-side Repository for accessing MongoDB Support Message collection.
    """
    _db = None

    @classmethod
    def get_db(cls):
        if cls._db is None:
            # Parse settings or use env directly
            mongo_uri = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
            db_name = os.getenv('DATABASE_NAME', 'casino_db')
            client = MongoClient(mongo_uri)
            cls._db = client[db_name]
        return cls._db

    @classmethod
    def get_history(cls, ticket_id):
        """Get all messages for a ticket, sorted by created_at asc"""
        db = cls.get_db()
        messages = list(db.support_messages.find({"ticket_id": ticket_id}).sort("created_at", 1))
        # Convert ObjectId to str
        for m in messages:
            m['id'] = str(m['_id'])
        return messages
