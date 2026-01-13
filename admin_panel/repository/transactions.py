from core.db import Database
from core.pagination import MongoPaginator
from datetime import datetime, timedelta

class TransactionRepository:
    @staticmethod
    def get_collection():
        return Database.get_db().transactions

    @classmethod
    def get_transactions(cls, page=1, page_size=25, user_id=None, type=None, status=None, date_from=None, date_to=None):
        query = {}
        
        if user_id:
            query["user_id"] = str(user_id)
        
        if type:
            query["type"] = type
            
        if status:
            query["status"] = status
            
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = date_from
            if date_to:
                date_filter["$lte"] = date_to
            query["created_at"] = date_filter

        sort = [("created_at", -1)]
        
        paginator = MongoPaginator(cls.get_collection(), query, page, page_size, sort)
        return paginator.get_context()

    @classmethod
    def get_transaction(cls, transaction_id):
        from bson import ObjectId
        try:
            return cls.get_collection().find_one({"_id": ObjectId(transaction_id)})
        except:
            return None

    @classmethod
    def get_stats_ggr(cls):
        """
        Calculate GGR = Total Deposits - Total Withdrawals (Completed only)
        """
        pipeline = [
            {"$match": {"status": {"$in": ["completed", "success", "paid", "confirmed"]}}},
            {"$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"}
            }}
        ]
        results = list(cls.get_collection().aggregate(pipeline))
        
        deposit = 0
        withdrawal = 0
        
        for r in results:
            if r["_id"] == "deposit":
                deposit = r["total"]
            elif r["_id"] == "withdrawal":
                withdrawal = r["total"]
                
        return deposit - withdrawal

    @classmethod
    def get_monthly_stats(cls):
        """
        Get total deposits and withdrawals for the current month.
        """
        now = datetime.utcnow()
        start_date = datetime(now.year, now.month, 1)
        
        pipeline = [
            {"$match": {
                "status": {"$in": ["completed", "success", "paid", "confirmed"]},
                "created_at": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"}
            }}
        ]
        
        results = list(cls.get_collection().aggregate(pipeline))
        stats = {"deposit": 0, "withdrawal": 0}
        
        for r in results:
            stats[r["_id"]] = r["total"]
            
        return stats
