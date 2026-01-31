"""Admin management service - business logic for admin CRUD operations."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import secrets

from app.core.security import hash_password
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.core.audit import log_action
from app.models.admin import AdminUser
from app.schemas.admin import CreateAdminRequest, UpdateAdminRequest, UpdateAdminStatusRequest


class AdminService:
    """Admin management service."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_admin(
        self,
        data: CreateAdminRequest,
        created_by: AdminUser,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> AdminUser:
        """Create a new admin user."""
        
        # Check if username already exists
        existing = await self.db.admin_users.find_one({"username": data.username})
        if existing:
            raise ConflictError("Username already exists")
        
        # Check if email already exists
        existing = await self.db.admin_users.find_one({"email": data.email})
        if existing:
            raise ConflictError("Email already exists")
        
        # Validate roles exist
        roles = await self.db.roles.find({"role_id": {"$in": data.roles}}).to_list(length=None)
        if len(roles) != len(data.roles):
            raise ValidationError("One or more roles do not exist")
        
        # Generate admin ID
        admin_id = f"admin_{secrets.token_hex(8)}"
        
        # Create admin user
        admin = AdminUser(
            admin_id=admin_id,
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            roles=data.roles,
            status="active",
            mfa_enabled=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Insert into database
        await self.db.admin_users.insert_one(
            admin.model_dump(by_alias=True, exclude={"id"})
        )
        
        # Log action
        await log_action(
            db=self.db,
            admin=created_by,
            action="admin.create",
            resource_type="admin",
            resource_id=admin_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            changes={"username": data.username, "email": data.email, "roles": data.roles}
        )
        
        return admin
    
    async def get_admin(self, admin_id: str) -> AdminUser:
        """Get admin by ID."""
        
        admin_doc = await self.db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc:
            raise NotFoundError("Admin not found")
        
        return AdminUser(**admin_doc)
    
    async def list_admins(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List admins with filters and pagination."""
        
        # Build query
        query = {}
        
        if status:
            query["status"] = status
        
        if role:
            query["roles"] = role
        
        if search:
            query["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await self.db.admin_users.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * page_size
        admins = await self.db.admin_users.find(query)\
            .sort("created_at", -1)\
            .skip(skip)\
            .limit(page_size)\
            .to_list(length=page_size)
        
        return {
            "items": [AdminUser(**admin) for admin in admins],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def update_admin(
        self,
        admin_id: str,
        data: UpdateAdminRequest,
        updated_by: AdminUser,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> AdminUser:
        """Update admin user."""
        
        # Get existing admin
        admin_doc = await self.db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc:
            raise NotFoundError("Admin not found")
        
        old_admin = AdminUser(**admin_doc)
        
        # Build update dict
        update_data = {"updated_at": datetime.utcnow()}
        changes = {}
        
        if data.email:
            # Check if email already exists for another admin
            existing = await self.db.admin_users.find_one({
                "email": data.email,
                "admin_id": {"$ne": admin_id}
            })
            if existing:
                raise ConflictError("Email already exists")
            
            update_data["email"] = data.email
            changes["email"] = {"old": old_admin.email, "new": data.email}
        
        if data.roles is not None:
            # Validate roles exist
            roles = await self.db.roles.find({"role_id": {"$in": data.roles}}).to_list(length=None)
            if len(roles) != len(data.roles):
                raise ValidationError("One or more roles do not exist")
            
            update_data["roles"] = data.roles
            changes["roles"] = {"old": old_admin.roles, "new": data.roles}
        
        # Update in database
        await self.db.admin_users.update_one(
            {"admin_id": admin_id},
            {"$set": update_data}
        )
        
        # Log action
        await log_action(
            db=self.db,
            admin=updated_by,
            action="admin.update",
            resource_type="admin",
            resource_id=admin_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            changes=changes
        )
        
        # Return updated admin
        return await self.get_admin(admin_id)
    
    async def update_status(
        self,
        admin_id: str,
        data: UpdateAdminStatusRequest,
        updated_by: AdminUser,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> AdminUser:
        """Update admin status (active/suspended)."""
        
        # Get existing admin
        admin_doc = await self.db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc:
            raise NotFoundError("Admin not found")
        
        old_admin = AdminUser(**admin_doc)
        
        # Prevent suspending yourself
        if admin_id == updated_by.admin_id:
            raise ValidationError("Cannot change your own status")
        
        # Update status
        await self.db.admin_users.update_one(
            {"admin_id": admin_id},
            {
                "$set": {
                    "status": data.status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log action
        await log_action(
            db=self.db,
            admin=updated_by,
            action="admin.update_status",
            resource_type="admin",
            resource_id=admin_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            changes={
                "status": {"old": old_admin.status, "new": data.status}
            },
            reason=data.reason,
            level="WARN"
        )
        
        return await self.get_admin(admin_id)
    
    async def delete_admin(
        self,
        admin_id: str,
        deleted_by: AdminUser,
        ip_address: str,
        user_agent: str,
        session_id: str
    ):
        """Soft delete admin user."""
        
        # Get existing admin
        admin_doc = await self.db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc:
            raise NotFoundError("Admin not found")
        
        # Prevent deleting yourself
        if admin_id == deleted_by.admin_id:
            raise ValidationError("Cannot delete your own account")
        
        # Soft delete
        await self.db.admin_users.update_one(
            {"admin_id": admin_id},
            {
                "$set": {
                    "status": "deleted",
                    "deleted_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log action
        await log_action(
            db=self.db,
            admin=deleted_by,
            action="admin.delete",
            resource_type="admin",
            resource_id=admin_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            level="CRITICAL"
        )
