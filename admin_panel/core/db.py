import logging
import environ
from pymongo import MongoClient
from django.conf import settings

logger = logging.getLogger(__name__)

env = environ.Env()

class Database:
    client = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            mongo_url = env("MONGODB_URL", default="mongodb://localhost:27017")
            db_name = env("DATABASE_NAME", default="casino_db")
            
            logger.info(f"Connecting to MongoDB: {db_name} at {mongo_url}")
            try:
                cls.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
                # Verify connection
                cls.client.server_info()
                cls.db = cls.client[db_name]
                logger.info("✅ Connected to MongoDB successfully")
            except Exception as e:
                logger.error(f"❌ Failed to connect to MongoDB: {e}")
                raise e

    @classmethod
    def get_db(cls):
        if cls.db is None:
            cls.connect()
        return cls.db

    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("Closed MongoDB connection")
