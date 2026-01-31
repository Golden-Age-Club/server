import asyncio
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from app.database import database
from app.core.permissions import SYSTEM_ROLES

async def seed():
    await database.connect()
    db = database.db
    
    print("Seeding roles...")
    for role_id, role_data in SYSTEM_ROLES.items():
        existing = await db.roles.find_one({"role_id": role_id})
        if not existing:
            await db.roles.insert_one({
                "role_id": role_id,
                "name": role_data["name"],
                "description": role_data["description"],
                "permissions": role_data["permissions"],
                "is_system_role": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            print(f"Created role: {role_id}")
        else:
            # Update permissions if they changed
            await db.roles.update_one(
                {"role_id": role_id},
                {"$set": {
                    "permissions": role_data["permissions"],
                    "updated_at": datetime.utcnow()
                }}
            )
            print(f"Updated role: {role_id}")
            
    print("Database seeding completed.")
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(seed())
