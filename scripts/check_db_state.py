import os
import sys
from pymongo import MongoClient
import environ

env = environ.Env()
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(base_dir, '.env'))

def check():
    mongo_url = env("MONGODB_URL", default="mongodb://localhost:27017")
    db_name = env("DATABASE_NAME", default="casino_db")
    
    client = MongoClient(mongo_url)
    db = client[db_name]
    coll = db.users
    
    # 1. Counts
    legacy_count = coll.count_documents({"_id": {"$type": "int"}})
    legacy_long_count = coll.count_documents({"_id": {"$type": "long"}})
    new_count = coll.count_documents({"_id": {"$type": "objectId"}})
    
    print(f"Legacy Users (int): {legacy_count}")
    print(f"Legacy Users (long): {legacy_long_count}")
    print(f"Migrated Users (ObjectId): {new_count}")
    
    # 2. Indices
    print("\nIndices:")
    for idx in coll.list_indexes():
        print(idx)

if __name__ == "__main__":
    check()
