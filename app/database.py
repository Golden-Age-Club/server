"""MongoDB database connection and management."""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database manager with connection pooling."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Establish MongoDB connection."""
        try:
            logger.info(f"Connecting to MongoDB: {settings.mongodb_url}")
            
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                minPoolSize=settings.mongodb_min_pool_size,
                maxPoolSize=settings.mongodb_max_pool_size,
                serverSelectionTimeoutMS=5000,
            )
            
            self.db = self.client[settings.mongodb_db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("MongoDB connection established successfully")
            
            # Create indexes
            await self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    async def _create_indexes(self):
        """Create database indexes for optimal performance."""
        logger.info("Creating database indexes...")
        
        # Admin Users indexes
        await self.db.admin_users.create_index("admin_id", unique=True)
        await self.db.admin_users.create_index("username", unique=True)
        await self.db.admin_users.create_index("email", unique=True)
        await self.db.admin_users.create_index("status")
        
        # Roles indexes
        await self.db.roles.create_index("role_id", unique=True)
        await self.db.roles.create_index("name", unique=True)
        
        # Permissions indexes
        await self.db.permissions.create_index("permission_id", unique=True)
        await self.db.permissions.create_index([("resource", 1), ("action", 1)], unique=True)
        
        # Audit Logs indexes
        await self.db.audit_logs.create_index([("timestamp", -1)])
        await self.db.audit_logs.create_index([("admin_id", 1), ("timestamp", -1)])
        await self.db.audit_logs.create_index([("resource_type", 1), ("resource_id", 1), ("timestamp", -1)])
        
        # TTL index for audit logs (7 years retention)
        await self.db.audit_logs.create_index(
            "timestamp",
            expireAfterSeconds=settings.audit_log_retention_days * 24 * 60 * 60
        )
        
        # Transactions indexes
        await self.db.transactions.create_index([("player_id", 1), ("created_at", -1)])
        await self.db.transactions.create_index("type")
        await self.db.transactions.create_index("status")
        await self.db.transactions.create_index("transaction_id", unique=True)
        
        # Bets indexes
        await self.db.bets.create_index([("player_id", 1), ("created_at", -1)])
        await self.db.bets.create_index([("game_id", 1), ("created_at", -1)])
        await self.db.bets.create_index("status")
        await self.db.bets.create_index("created_at")
        
        logger.info("Database indexes created successfully")

    async def health_check(self) -> bool:
        """Check database connection health."""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def get_collection(self, name: str):
        """Get a collection from the database."""
        return self.db[name]


# Global database instance
database = Database()


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance."""
    return database.db
