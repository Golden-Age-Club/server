"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import database
from app.api.v1 import api_router
from app.core.exceptions import AppException
from app.middleware.error_handler import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from app.middleware.audit import AuditMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await database.connect()
    
    yield
    
    # Shutdown
    await database.disconnect()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Slot Machine Admin Backend API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    db_healthy = await database.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "database": "connected" if db_healthy else "disconnected"
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled in production"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
