from bson import ObjectId
from core.db import Database
from core.pagination import MongoPaginator
from datetime import datetime

class UserRepository:
    @staticmethod
    def get_collection():
        return Database.get_db().users

    @classmethod
    def get_users(cls, page=1, page_size=25, search=None, sort_by="created_at", sort_desc=True, filters=None):
        query = {}
        if filters:
            query.update(filters)
        
        if search:
            # Search by Email, Username, Name, or Telegram ID
            search_query = []
            
            # 1. Exact match on telegram_id (if generic number)
            if search.isdigit():
                 search_query.append({"telegram_id": int(search)})

            # 2. Regex matches
            search_query.append({"username": {"$regex": search, "$options": "i"}})
            search_query.append({"email": {"$regex": search, "$options": "i"}})
            search_query.append({"first_name": {"$regex": search, "$options": "i"}})
            search_query.append({"last_name": {"$regex": search, "$options": "i"}})
            
            # 3. ObjectId match? (If search is valid ObjectId)
            try:
                search_query.append({"_id": ObjectId(search)})
            except:
                pass
            
            if len(search_query) == 1:
                query.update(search_query[0])
            elif len(search_query) > 1:
                if "$or" in query:
                    # Merge existing $or
                    query["$and"] = [{"$or": search_query}, {"$or": query.pop("$or")}]
                else:
                    query["$or"] = search_query

        sort_dir = -1 if sort_desc else 1
        sort = [(sort_by, sort_dir)]

        paginator = MongoPaginator(cls.get_collection(), query, page, page_size, sort)
        return paginator.get_context()

    @classmethod
    def get_user_by_id(cls, user_id):
        # Support ObjectId lookup
        try:
            doc = cls.get_collection().find_one({"_id": ObjectId(user_id)})
            if doc:
                doc['id'] = str(doc['_id'])
            return doc
        except:
            return None

    @classmethod
    def update_user(cls, user_id, data):
        """
        Update allowed fields.
        data: dict of fields to update.
        """
        try:
            cls.get_collection().update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {**data, "updated_at": datetime.utcnow()}}
            )
            return True
        except Exception:
            return False

    @classmethod
    def get_total_users(cls):
        return cls.get_collection().count_documents({})
