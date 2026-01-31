from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import logging
from datetime import datetime

from app.database import database
from app.models.audit import AuditLogInDB
from app.dependencies import get_client_ip, get_user_agent

logger = logging.getLogger(__name__)

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We only log state-changing operations (POST, PATCH, PUT, DELETE)
        # and we don't log the auth routes (login) as they handle their own logs if needed
        is_audit_method = request.method in ["POST", "PATCH", "PUT", "DELETE"]
        is_auth_route = "/auth/" in request.url.path
        
        response = await call_next(request)
        
        if is_audit_method and not is_auth_route and response.status_code < 400:
            # We use a background task to not block the response
            # But for "Readiness", we'll just implement it here or via a simple await
            try:
                # Check for admin user in request state
                admin = getattr(request.state, "admin", None)
                if admin:
                    # Extract action from URL path
                    path_parts = request.url.path.strip("/").split("/")
                    # Usually /api/v1/admin/resource/...
                    resource = path_parts[3] if len(path_parts) > 3 else "unknown"
                    action = f"{resource}.{request.method.lower()}"
                    
                    audit_entry = {
                        "timestamp": datetime.utcnow(),
                        "level": "INFO",
                        "admin_id": admin.admin_id,
                        "admin_username": admin.username,
                        "action": action,
                        "resource_type": resource,
                        "resource_id": path_parts[4] if len(path_parts) > 4 else "new",
                        "ip_address": get_client_ip(request),
                        "user_agent": get_user_agent(request),
                        "changes": {}, # In a more complex setup, we'd capture the body
                        "session_id": getattr(request.state, "session_id", "unknown")
                    }
                    
                    # Store in DB
                    db = database.db
                    if db is not None:
                        await db.audit_logs.insert_one(audit_entry)
                        
            except Exception as e:
                logger.error(f"Failed to record audit log: {e}")
                
        return response
