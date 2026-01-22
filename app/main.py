from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.core.logging_config import setup_logging
from app.middleware.request_id import RequestIDMiddleware
from app.routes import wallet, webhook, auth, support, casino, unified_callback
from app.config import get_settings
import logging

from fastapi.security import HTTPBearer

settings = get_settings()
security = HTTPBearer()

# Add to verify_jwt_token logic or app description later?
# Easiest is to add it to routes or global dependency if we want the lock icon for everything.
# But for now, let's just use it in main.py to hint OpenAPI.

setup_logging(log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
logger = logging.getLogger(__name__)

# ... (omitted)


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Golden Age USDT Wallet API",
    description="USDT Wallet Integration with CCPayment and Telegram Authentication",
    version="1.0.0",
    contact={
        "name": "Golden Age Support",
        "email": "support@goldenage.com",
    },
    license_info={
        "name": "Proprietary",
    },
)

app.add_middleware(RequestIDMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    logger.info("🚀 Starting Golden Age USDT Wallet API...")
    await connect_to_mongo()
    logger.info(f"Testing mode: {settings.TESTING_MODE}")
    logger.info(f"Allowed origins: {allowed_origins}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"Log format: {settings.LOG_FORMAT}")
    # Removed aggressive keep-alive loop to prevent resource exhaustion
    logger.info("✅ Application started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Shutting down application...")
    await close_mongo_connection()
    logger.info("✅ Application shutdown complete")

# Include routers
app.include_router(auth.router)
app.include_router(wallet.router)
app.include_router(webhook.router)
app.include_router(casino.router)
app.include_router(unified_callback.router)
app.include_router(support.router)

@app.get("/")
async def root():
    return {
        "message": "Golden Age USDT Wallet API",
        "version": "1.0.0",
        "testing_mode": settings.TESTING_MODE,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint with database connectivity verification
    """
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "unknown",
            "payment_provider": "unknown"
        }
    }
    
    try:
        # Check database connectivity
        db = await get_database()
        await db.command('ping')
        health_status["checks"]["database"] = "connected"
        logger.debug("Health check: database connected")
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"
        logger.error(f"Health check failed: {e}")
    
    # Check payment provider status
    if settings.TESTING_MODE:
        health_status["checks"]["payment_provider"] = "mock"
    else:
        health_status["checks"]["payment_provider"] = "configured"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
