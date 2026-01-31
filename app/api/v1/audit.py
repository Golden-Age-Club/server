from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import get_database
from app.dependencies import get_current_admin
from app.core.permissions import check_permission
from app.models.audit import AuditLogInDB
from app.schemas.common import ResponseModel

router = APIRouter()

@router.get("/logs", response_model=ResponseModel)
async def list_audit_logs(
    admin_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    level: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_admin=Depends(get_current_admin)
):
    """List administrative audit logs with filters."""
    if not await check_permission(current_admin, "audit:read", db):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = {}
    if admin_id:
        query["admin_id"] = admin_id
    if action:
        query["action"] = action
    if resource_type:
        query["resource_type"] = resource_type
    if level:
        query["level"] = level
        
    total = await db.audit_logs.count_documents(query)
    skip = (page - 1) * page_size
    cursor = db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(page_size)
    logs = await cursor.to_list(length=page_size)
    
    # Extract data from DB objects
    result_logs = []
    for log in logs:
        log["id"] = str(log["_id"])
        del log["_id"]
        result_logs.append(log)
    
    return {
        "success": True,
        "data": result_logs,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }
