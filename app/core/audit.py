"""Audit logging utilities."""

from datetime import datetime
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import re

from app.models.audit import AuditLog
from app.models.admin import AdminUser


# Sensitive fields to mask in audit logs
SENSITIVE_FIELDS = {
    "password", "password_hash", "secret", "mfa_secret",
    "token", "access_token", "refresh_token", "api_key"
}


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive fields in data dictionary."""
    if not isinstance(data, dict):
        return data
    
    masked = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
            masked[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value)
        elif isinstance(value, list):
            masked[key] = [mask_sensitive_data(item) if isinstance(item, dict) else item for item in value]
        else:
            masked[key] = value
    
    return masked


async def log_action(
    db: AsyncIOMotorDatabase,
    admin: AdminUser,
    action: str,
    resource_type: str,
    resource_id: str,
    ip_address: str,
    user_agent: str,
    session_id: str,
    changes: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    level: str = "INFO"
):
    """Create an audit log entry."""
    
    # Mask sensitive data in changes
    masked_changes = mask_sensitive_data(changes) if changes else {}
    
    audit_log = AuditLog(
        timestamp=datetime.utcnow(),
        level=level,
        admin_id=admin.admin_id,
        admin_username=admin.username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        changes=masked_changes,
        reason=reason,
        session_id=session_id
    )
    
    # Insert into database
    await db.audit_logs.insert_one(audit_log.model_dump(by_alias=True, exclude={"id"}))


async def log_financial_action(
    db: AsyncIOMotorDatabase,
    admin: AdminUser,
    action: str,
    resource_type: str,
    resource_id: str,
    ip_address: str,
    user_agent: str,
    session_id: str,
    amount: float,
    currency: str,
    changes: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None
):
    """Create a financial audit log entry (separate collection for compliance)."""
    
    financial_log = {
        "timestamp": datetime.utcnow(),
        "level": "CRITICAL",
        "admin_id": admin.admin_id,
        "admin_username": admin.username,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "amount": amount,
        "currency": currency,
        "changes": mask_sensitive_data(changes) if changes else {},
        "reason": reason,
        "session_id": session_id
    }
    
    # Insert into financial audit logs (immutable, never deleted)
    await db.financial_audit_logs.insert_one(financial_log)
    
    # Also log in regular audit logs
    await log_action(
        db=db,
        admin=admin,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
        changes=changes,
        reason=reason,
        level="CRITICAL"
    )
