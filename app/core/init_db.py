"""
Database initialization and index management
"""
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


async def init_indexes(db: AsyncIOMotorDatabase):
    """
    Create database indexes for optimal performance
    
    Args:
        db: MongoDB database instance
    """
    logger.info("Initializing database indexes...")
    
    try:
        # Users collection indexes
        logger.info("Creating users collection indexes...")
        
        # Unique index on telegram_id (already used as _id, but explicit for clarity)
        await db.users.create_index("telegram_id", unique=True)
        
        # Index on username for lookups
        await db.users.create_index("username", sparse=True)
        
        # Index on is_active for filtering active users
        await db.users.create_index("is_active")
        
        logger.info("✓ Users indexes created")
        
        # Transactions collection indexes
        logger.info("Creating transactions collection indexes...")
        
        # Index on user_id for user transaction queries
        await db.transactions.create_index("user_id")
        
        # Unique index on merchant_order_id for webhook lookups
        await db.transactions.create_index("merchant_order_id", unique=True, sparse=True)
        
        # Index on status for filtering by transaction status
        await db.transactions.create_index("status")
        
        # Compound index on user_id + created_at for sorted user transaction history
        await db.transactions.create_index([
            ("user_id", 1),
            ("created_at", -1)
        ])
        
        # Compound index on user_id + status for filtering user's pending/completed transactions
        await db.transactions.create_index([
            ("user_id", 1),
            ("status", 1)
        ])
        
        # Index on created_at for time-based queries
        await db.transactions.create_index("created_at")
        
        logger.info("✓ Transactions indexes created")
        
        logger.info("✅ All database indexes initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        raise


async def get_index_info(db: AsyncIOMotorDatabase) -> dict:
    """
    Get information about existing indexes
    
    Args:
        db: MongoDB database instance
        
    Returns:
        Dictionary with index information for each collection
    """
    try:
        users_indexes = await db.users.index_information()
        transactions_indexes = await db.transactions.index_information()
        
        return {
            "users": users_indexes,
            "transactions": transactions_indexes
        }
    except Exception as e:
        logger.error(f"Error getting index info: {e}")
        return {}
