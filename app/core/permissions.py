"""Role-Based Access Control (RBAC) implementation."""

from typing import List, Set, Optional
from functools import wraps
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import AuthorizationError
from app.models.admin import AdminUser


# System role definitions with permissions
SYSTEM_ROLES = {
    "super_admin": {
        "name": "Super Admin",
        "description": "Full system access",
        "permissions": ["*:*"],  # Wildcard for all permissions
        "is_system_role": True
    },
    "operator": {
        "name": "Operator",
        "description": "General operations and user management",
        "permissions": [
            "user:read", "user:write",
            "bet:read",
            "game:read",
            "vip:read", "vip:write",
            "bonus:read", "bonus:write",
            "report:read"
        ],
        "is_system_role": True
    },
    "finance_manager": {
        "name": "Finance Manager",
        "description": "Manages financial operations",
        "permissions": [
            "wallet:read", "wallet:write", "wallet:approve",
            "deposit:read", "deposit:write",
            "withdrawal:read", "withdrawal:approve",
            "finance:read", "finance:write",
            "report:read", "report:export"
        ],
        "is_system_role": True
    },
    "risk_manager": {
        "name": "Risk Manager",
        "description": "Manages risk control and fraud prevention",
        "permissions": [
            "risk:read", "risk:write", "risk:manage",
            "user:read", "user:write",
            "report:read"
        ],
        "is_system_role": True
    },
    "customer_support": {
        "name": "Customer Support",
        "description": "Handles customer inquiries and basic user management",
        "permissions": [
            "user:read",
            "wallet:read",
            "bet:read",
            "report:read"
        ],
        "is_system_role": True
    },
    "marketing_manager": {
        "name": "Marketing Manager",
        "description": "Manages promotions and VIP programs",
        "permissions": [
            "bonus:read", "bonus:write",
            "vip:read", "vip:write",
            "user:read",
            "report:read"
        ],
        "is_system_role": True
    },
    "analyst": {
        "name": "Analyst",
        "description": "Read-only access to reports and analytics",
        "permissions": [
            "report:read", "report:export"
        ],
        "is_system_role": True
    },
    "game_manager": {
        "name": "Game Manager",
        "description": "Manages game catalog and configuration",
        "permissions": [
            "game:read", "game:write",
            "bet:read",
            "report:read"
        ],
        "is_system_role": True
    }
}


# All available permissions
ALL_PERMISSIONS = {
    # Admin management
    "admin:read": "View admin users",
    "admin:write": "Create and update admin users",
    "admin:delete": "Delete admin users",
    
    # Role management
    "role:read": "View roles and permissions",
    "role:write": "Create and update roles",
    
    # User management
    "user:read": "View user information",
    "user:write": "Update user status and information",
    
    # Wallet & Finance
    "wallet:read": "View wallet balances and transactions",
    "wallet:write": "Perform manual balance adjustments",
    "wallet:approve": "Approve manual adjustments (dual approval)",
    
    # Deposits
    "deposit:read": "View deposit records",
    "deposit:write": "Manually confirm deposits",
    
    # Withdrawals
    "withdrawal:read": "View withdrawal requests",
    "withdrawal:approve": "Approve or reject withdrawals",
    
    # Finance (general)
    "finance:read": "View financial reports",
    "finance:write": "Perform financial operations",
    
    # Bets & Games
    "bet:read": "View bet records",
    "game:read": "View game catalog",
    "game:write": "Enable/disable games and update configuration",
    
    # VIP Management
    "vip:read": "View VIP tiers and high-value players",
    "vip:write": "Update VIP tiers and manually adjust user VIP levels",
    
    # Risk Control
    "risk:read": "View risk rules and triggers",
    "risk:write": "Create and update risk rules",
    "risk:manage": "Apply user restrictions and resolve triggers",
    
    # Bonus & Promotion
    "bonus:read": "View promotions and bonus status",
    "bonus:write": "Create promotions and grant bonuses",
    
    # Reporting
    "report:read": "View reports and dashboards",
    "report:export": "Export data to CSV/Excel",
    "dashboard:read": "View real-time dashboard statistics",
    
    # System & Audit
    "audit:read": "View audit logs",
    "audit:export": "Export audit logs",
    "system:read": "View system configuration",
    "system:write": "Update system configuration",
    "system:admin": "Manage admin accounts and roles"
}


async def get_admin_permissions(admin_user: AdminUser, db: AsyncIOMotorDatabase) -> Set[str]:
    """Get all permissions for an admin user based on their roles."""
    permissions = set()
    
    # Fetch all roles for the admin
    roles = await db.roles.find({"role_id": {"$in": admin_user.roles}}).to_list(length=None)
    
    for role in roles:
        role_permissions = role.get("permissions", [])
        
        # Check for wildcard permission (super admin)
        if "*:*" in role_permissions:
            return set(ALL_PERMISSIONS.keys())
        
        permissions.update(role_permissions)
    
    return permissions


async def check_permission(admin_user: AdminUser, required_permission: str, db: AsyncIOMotorDatabase) -> bool:
    """Check if admin user has a specific permission."""
    admin_permissions = await get_admin_permissions(admin_user, db)
    
    # Check for exact match
    if required_permission in admin_permissions:
        return True
    
    # Check for wildcard permission
    if "*:*" in admin_permissions:
        return True
    
    # Check for resource-level wildcard (e.g., user:* grants user:read, user:write)
    resource = required_permission.split(":")[0]
    if f"{resource}:*" in admin_permissions:
        return True
    
    return False


def require_permission(permission: str):
    """Decorator to require a specific permission for an endpoint."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_admin and db from kwargs
            current_admin = kwargs.get("current_admin")
            db = kwargs.get("db")
            
            if not current_admin or not db:
                raise AuthorizationError("Authentication required")
            
            has_permission = await check_permission(current_admin, permission, db)
            
            if not has_permission:
                raise AuthorizationError(
                    f"Insufficient permissions. Required: {permission}",
                    details={"required_permission": permission}
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*permissions: str):
    """Decorator to require any of the specified permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_admin = kwargs.get("current_admin")
            db = kwargs.get("db")
            
            if not current_admin or not db:
                raise AuthorizationError("Authentication required")
            
            for permission in permissions:
                if await check_permission(current_admin, permission, db):
                    return await func(*args, **kwargs)
            
            raise AuthorizationError(
                f"Insufficient permissions. Required any of: {', '.join(permissions)}",
                details={"required_permissions": list(permissions)}
            )
        
        return wrapper
    return decorator


def require_all_permissions(*permissions: str):
    """Decorator to require all of the specified permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_admin = kwargs.get("current_admin")
            db = kwargs.get("db")
            
            if not current_admin or not db:
                raise AuthorizationError("Authentication required")
            
            for permission in permissions:
                if not await check_permission(current_admin, permission, db):
                    raise AuthorizationError(
                        f"Insufficient permissions. Required all of: {', '.join(permissions)}",
                        details={"required_permissions": list(permissions)}
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
