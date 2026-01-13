import os
import sys
import logging
from pymongo import MongoClient
from bson import ObjectId
import environ

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load Env
env = environ.Env()
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(base_dir, '.env'))

def migrate():
    mongo_url = env("MONGODB_URL", default="mongodb://localhost:27017")
    db_name = env("DATABASE_NAME", default="casino_db")
    
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    users_coll = db.users
    tx_coll = db.transactions
    
    logger.info(f"Starting migration on {db_name}...")
    
    # DROP INDICES FIRST to avoid conflicts or blockages
    try:
        users_coll.drop_index("telegram_id_1")
        logger.info("Dropped existing telegram_id_1 index.")
    except Exception:
        pass

    try:
        users_coll.drop_index("email_1")
        logger.info("Dropped existing email_1 index.")
    except Exception:
        pass
    
    # 1. Fetch all users
    legacy_users = list(users_coll.find({"_id": {"$type": "int"}}))
    legacy_users_long = list(users_coll.find({"_id": {"$type": "long"}}))
    all_legacy = legacy_users + legacy_users_long
    
    logger.info(f"DEBUG: Found {len(legacy_users)} int-type users.")
    logger.info(f"DEBUG: Found {len(legacy_users_long)} long-type users.")
    
    # Deduplicate
    legacy_map = {u["_id"]: u for u in all_legacy}
    unique_legacy_users = list(legacy_map.values())
    
    logger.info(f"Processing {len(unique_legacy_users)} unique legacy users...")
    
    migrated_count = 0
    
    for user in legacy_users:
        old_id = user["_id"]
        
        # Check if already migrated (sanity check if run multiple times - logic below handles it)
        # But here we are creating NEW documents.
        
        # 1. Generate new ID
        new_id = ObjectId()
        
        # 2. Prepare new user document
        new_user = user.copy()
        new_user["_id"] = new_id
        new_user["telegram_id"] = int(old_id) # Preserve old ID as telegram_id
        new_user["email"] = None
        new_user["password_hash"] = None
        
        try:
            # 3. Insert new user
            users_coll.insert_one(new_user)
            
            # 4. Update Transactions
            # Transactions stored user_id as string representation of the int
            # e.g. "12345" -> "507f1f77bcf86cd799439011"
            res = tx_coll.update_many(
                {"user_id": str(old_id)},
                {"$set": {"user_id": str(new_id)}}
            )
            
            # 5. Delete old user
            users_coll.delete_one({"_id": old_id})
            
            logger.info(f"Migrated User {old_id} -> {new_id}. Transactions updated: {res.modified_count}")
            migrated_count += 1
            
        except Exception as e:
            logger.error(f"Failed to migrate user {old_id}: {e}")
            # Identify cleanup?
            # If insert succeeded but update failed, we have duplicate user.
            # For simplicity in this script, manual cleanup might be needed if it crashes mid-loop.
            continue

    logger.info(f"Migration complete. Migrated {migrated_count} users.")
    
    # Create Indices
    logger.info("Creating indices...")
    users_coll.create_index("telegram_id", unique=True, sparse=True)
    users_coll.create_index("email", unique=True, sparse=True)
    logger.info("Indices created.")

if __name__ == "__main__":
    print("WARNING: This script will modify your database schema.")
    print("It converts 'Integer IDs' to 'ObjectId' and updates transactions.")
    
    if len(sys.argv) > 1 and sys.argv[1] == "-y":
        confirm = "yes"
    else:
        confirm = input("Type 'yes' to proceed: ")
        
    if confirm == "yes":
        migrate()
    else:
        print("Aborted.")
