import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import connect_to_mongo
from app.repositories.user import UserRepository

async def create_demo_user():
    print("Connecting to database...")
    await connect_to_mongo()
    from app.core.database import get_database
    db = await get_database()
    
    user_repo = UserRepository(db)
    
    demo_user_id = 777777777
    
    # Check if exists
    user = await user_repo.get_by_telegram_id(demo_user_id)
    
    if user:
        print(f"Demo user {demo_user_id} already exists.")
        print(f"Current Balance: {user.get('balance', 0)}")
    else:
        print(f"Creating demo user {demo_user_id}...")
        user_data = {
            "telegram_id": demo_user_id,
            "username": "demo_tester",
            "first_name": "Demo",
            "last_name": "User",
            "language_code": "en",
            "is_premium": True
        }
        await user_repo.create_user(user_data)
        
        # Add some balance
        await user_repo.update_balance(str(demo_user_id), 1000.0)
        print("Demo user created successfully.")
        
    print("-" * 30)
    print(f"User ID: {demo_user_id}")
    print(f"Username: demo_tester")
    print("Password: N/A (Telegram Auth)")
    print("-" * 30)

if __name__ == "__main__":
    asyncio.run(create_demo_user())
