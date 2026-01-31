"""Database seeding script - creates initial data."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import secrets

from app.config import settings
from app.core.security import hash_password
from app.core.permissions import SYSTEM_ROLES, ALL_PERMISSIONS


async def seed_database():
    """Seed database with initial data."""
    
    print("🌱 Starting database seeding...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # 1. Create Permissions
        print("\n📋 Creating permissions...")
        permissions_collection = db.permissions
        
        # Clear existing permissions
        await permissions_collection.delete_many({})
        
        permissions = []
        for perm_id, description in ALL_PERMISSIONS.items():
            resource, action = perm_id.split(":")
            permissions.append({
                "permission_id": perm_id,
                "resource": resource,
                "action": action,
                "description": description,
                "created_at": datetime.utcnow()
            })
        
        if permissions:
            await permissions_collection.insert_many(permissions)
            print(f"✅ Created {len(permissions)} permissions")
        
        # 2. Create System Roles
        print("\n👥 Creating system roles...")
        roles_collection = db.roles
        
        # Clear existing system roles
        await roles_collection.delete_many({"is_system_role": True})
        
        roles = []
        for role_id, role_data in SYSTEM_ROLES.items():
            roles.append({
                "role_id": role_id,
                "name": role_data["name"],
                "description": role_data["description"],
                "permissions": role_data["permissions"],
                "is_system_role": role_data["is_system_role"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        if roles:
            await roles_collection.insert_many(roles)
            print(f"✅ Created {len(roles)} system roles")
        
        # 3. Create Initial Super Admin
        print("\n👤 Creating initial super admin...")
        admins_collection = db.admin_users
        
        # Check if super admin already exists
        existing_admin = await admins_collection.find_one({
            "username": settings.initial_admin_username
        })
        
        if existing_admin:
            print(f"⚠️  Super admin '{settings.initial_admin_username}' already exists")
        else:
            admin_id = f"admin_{secrets.token_hex(8)}"
            
            super_admin = {
                "admin_id": admin_id,
                "username": settings.initial_admin_username,
                "email": settings.initial_admin_email,
                "password_hash": hash_password(settings.initial_admin_password),
                "mfa_secret": None,
                "mfa_enabled": False,
                "roles": ["super_admin"],
                "status": "active",
                "last_login": None,
                "failed_login_attempts": 0,
                "locked_until": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "deleted_at": None
            }
            
            await admins_collection.insert_one(super_admin)
            print(f"✅ Created super admin: {settings.initial_admin_username}")
            print(f"   Email: {settings.initial_admin_email}")
            print(f"   Password: {settings.initial_admin_password}")
            print(f"   ⚠️  CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN!")
        
        # 4. Create Indexes
        print("\n🔍 Creating indexes...")
        
        # Admin Users indexes
        await admins_collection.create_index("admin_id", unique=True)
        await admins_collection.create_index("username", unique=True)
        await admins_collection.create_index("email", unique=True)
        await admins_collection.create_index("status")
        
        # Roles indexes
        await roles_collection.create_index("role_id", unique=True)
        await roles_collection.create_index("name", unique=True)
        
        # Permissions indexes
        await permissions_collection.create_index("permission_id", unique=True)
        await permissions_collection.create_index([("resource", 1), ("action", 1)], unique=True)
        
        # Audit Logs indexes
        audit_logs_collection = db.audit_logs
        await audit_logs_collection.create_index([("timestamp", -1)])
        await audit_logs_collection.create_index([("admin_id", 1), ("timestamp", -1)])
        await audit_logs_collection.create_index([("resource_type", 1), ("resource_id", 1), ("timestamp", -1)])
        
        # TTL index for audit logs (7 years retention)
        await audit_logs_collection.create_index(
            "timestamp",
            expireAfterSeconds=settings.audit_log_retention_days * 24 * 60 * 60
        )
        
        print("✅ Created all indexes")
        
        # 5. Set up Schema Validation
        print("\n📝 Setting up schema validation...")
        
        # Admin Users validation
        await db.command({
            "collMod": "admin_users",
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["admin_id", "username", "email", "password_hash", "roles", "status"],
                    "properties": {
                        "admin_id": {"bsonType": "string"},
                        "username": {"bsonType": "string", "minLength": 3},
                        "email": {"bsonType": "string"},
                        "password_hash": {"bsonType": "string"},
                        "roles": {"bsonType": "array", "items": {"bsonType": "string"}},
                        "status": {"enum": ["active", "suspended", "deleted"]},
                        "mfa_enabled": {"bsonType": "bool"}
                    }
                }
            },
            "validationLevel": "moderate"
        })
        
        print("✅ Schema validation configured")
        
        print("\n✨ Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Permissions: {len(permissions)}")
        print(f"   - System Roles: {len(roles)}")
        print(f"   - Super Admin: {settings.initial_admin_username}")
        print("\n🚀 You can now start the application!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
