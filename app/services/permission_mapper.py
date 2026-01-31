"""Permission mapping service - converts backend permissions to frontend format."""

from typing import List, Set
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.admin import AdminUser
from app.core.permissions import get_admin_permissions


# Map backend permissions to frontend permission names
# Frontend uses simplified permission names for routing
BACKEND_TO_FRONTEND_PERMISSIONS = {
    # Dashboard
    "report:read": "dashboard",
    
    # Users
    "user:read": "users",
    "user:write": "users",
    
    # Finance (Wallet & Finance)
    "wallet:read": "finance",
    "wallet:write": "finance",
    "wallet:approve": "finance",
    "deposit:read": "finance",
    "deposit:write": "finance",
    "withdrawal:read": "finance",
    "withdrawal:approve": "finance",
    "finance:read": "finance",
    "finance:write": "finance",
    
    # Bets & Games
    "bet:read": "bets",
    "game:read": ["bets", "games"],
    "game:write": "games",
    
    # VIP
    "vip:read": "vip",
    "vip:write": "vip",
    
    # Risk Control
    "risk:read": "risk",
    "risk:write": "risk",
    "risk:manage": "risk",
    
    # Promotions (Bonus & Promotions)
    "bonus:read": "promotions",
    "bonus:write": "promotions",
    
    # Reports
    "report:export": "reports",
    
    # System (System & Logs, Admin Management)
    "admin:read": "system",
    "admin:write": "system",
    "admin:delete": "system",
    "role:read": "system",
    "role:write": "system",
    "audit:read": "system",
    "audit:export": "system",
    "system:read": "system",
    "system:write": "system",
    "system:admin": "system",
}

# All possible frontend permissions
ALL_FRONTEND_PERMISSIONS = [
    "dashboard",
    "users",
    "finance",
    "bets",
    "games",
    "vip",
    "risk",
    "promotions",
    "reports",
    "system",
]

# Role name aliases for frontend compatibility
ROLE_ALIASES = {
    "finance_manager": "finance",
    "risk_manager": "risk",
    "customer_support": "support",
    "marketing_manager": "marketing",
    "game_manager": "games",
    "analyst": "analyst",
    "super_admin": "super_admin",
}


async def get_frontend_permissions(admin: AdminUser, db: AsyncIOMotorDatabase) -> List[str]:
    """
    Convert backend permissions to frontend permission format.
    
    Frontend uses simplified permission names for route protection:
    - dashboard, users, finance, bets, games, vip, risk, promotions, reports, system
    
    Backend has granular permissions like:
    - user:read, wallet:write, bet:read, etc.
    
    This function maps backend permissions to frontend format.
    """
    # Get backend permissions
    backend_perms = await get_admin_permissions(admin, db)
    
    # Check for super admin (wildcard permission)
    if "*:*" in backend_perms:
        return ALL_FRONTEND_PERMISSIONS
    
    # Map backend permissions to frontend
    frontend_perms = set()
    
    for backend_perm in backend_perms:
        # Check for resource-level wildcard (e.g., user:*)
        if backend_perm.endswith(":*"):
            resource = backend_perm.split(":")[0]
            # Add all frontend permissions related to this resource
            for bp, fp in BACKEND_TO_FRONTEND_PERMISSIONS.items():
                if bp.startswith(f"{resource}:"):
                    if isinstance(fp, list):
                        frontend_perms.update(fp)
                    else:
                        frontend_perms.add(fp)
            continue
        
        # Direct mapping
        mapped = BACKEND_TO_FRONTEND_PERMISSIONS.get(backend_perm)
        if mapped:
            if isinstance(mapped, list):
                frontend_perms.update(mapped)
            else:
                frontend_perms.add(mapped)
    
    return sorted(list(frontend_perms))


def get_primary_role_alias(roles: List[str]) -> str:
    """
    Get the primary role alias for frontend.
    
    Frontend expects role names like: super_admin, operator, finance, risk, support
    Backend has: super_admin, finance_manager, risk_manager, customer_support, etc.
    
    This function returns the frontend-compatible role name.
    """
    if not roles:
        return "support"  # Default role
    
    # Get first role and map to alias
    primary_role = roles[0]
    return ROLE_ALIASES.get(primary_role, primary_role)


def get_all_role_aliases(roles: List[str]) -> List[str]:
    """Get all role aliases for frontend."""
    return [ROLE_ALIASES.get(role, role) for role in roles]
