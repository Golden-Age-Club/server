from config.settings import DATABASES
from pymongo import MongoClient
import os
from bson import ObjectId

class TicketRepository:
    """
    Django-side Repository for accessing MongoDB Ticket collection.
    Connects directly to MongoDB, consistent with other Django repos in this project.
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
    def get_all_open(cls):
        """Get all tickets with status 'open', sorted by updated_at desc"""
        db = cls.get_db()
        tickets = list(db.tickets.find({"status": "open"}).sort("updated_at", -1))
        # Convert ObjectId to str for template
        for t in tickets:
            t['id'] = str(t['_id'])
        return tickets

    @classmethod
    def get_by_id(cls, ticket_id):
        """Get ticket details by ID"""
        db = cls.get_db()
        try:
            ticket = db.tickets.find_one({"_id": ObjectId(ticket_id)})
            if ticket:
                ticket['id'] = str(ticket['_id'])
            return ticket
        except:
            return None

    @classmethod
    def resolve(cls, ticket_id):
        """Mark ticket as resolved"""
        db = cls.get_db()
        from datetime import datetime
        try:
            result = db.tickets.update_one(
                {"_id": ObjectId(ticket_id)},
                {"$set": {
                    "status": "resolved",
                    "updated_at": datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except:
            return False
