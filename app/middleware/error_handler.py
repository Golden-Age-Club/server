"""Global error handler middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "meta": None,
            "error": {
                "code": exc.__class__.__name__.upper(),
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "meta": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()}
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "meta": None,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {}
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "meta": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }
        }
    )
