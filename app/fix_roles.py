from app.database import database
import asyncio

async def update_roles():
    print("Connecting to database...")
    await database.connect()
    
    permissions = [
        "risk:read", "risk:write", "risk:manage", 
        "bonus:read", "bonus:write", 
        "promotions:read", "promotions:write"
    ]
    
    print(f"Updating super_admin with permissions: {permissions}")
    result = await database.db.roles.update_one(
        {"role_id": "super_admin"},
        {"$addToSet": {"permissions": {"$each": permissions}}}
    )
    
    print(f"Matched {result.matched_count} document, modified {result.modified_count}")
    
    # Also update the system roles dict internally if needed (though DB is source of truth)
    print("Update complete.")
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(update_roles())
