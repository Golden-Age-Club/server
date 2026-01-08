from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def get_database():
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        maxPoolSize=50,  # Maximum connections in pool
        minPoolSize=10,  # Minimum connections in pool
        serverSelectionTimeoutMS=5000  # Timeout for server selection
    )
    print(f"Connected to MongoDB: {settings.MONGODB_URL}")
    
    # Initialize database indexes
    try:
        from app.core.init_db import init_indexes
        database = db.client[settings.DATABASE_NAME]
        await init_indexes(database)
    except Exception as e:
        print(f"Warning: Failed to initialize indexes: {e}")

async def close_mongo_connection():
    db.client.close()
    print("Closed MongoDB connection")