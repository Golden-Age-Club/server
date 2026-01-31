"""Common schemas used across the application."""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class ResponseModel(BaseModel):
    """Standard API response model."""
    
    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(None, description="Response data")
    meta: Optional[Dict[str, Any]] = Field(None, description="Metadata (pagination, etc.)")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "123", "name": "Example"},
                "meta": {"page": 1, "total": 100},
                "error": None
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    
    page: int
    page_size: int
    total: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = False
    data: None = None
    meta: None = None
    error: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "data": None,
                "meta": None,
                "error": {
                    "code": "AUTHENTICATION_ERROR",
                    "message": "Invalid credentials",
                    "details": {}
                }
            }
        }
