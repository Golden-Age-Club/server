import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from app.main import app
from app.core.database import db, get_database
from app.config import get_settings
from app.services.ccpayment import PaymentProvider

settings = get_settings()
settings.TESTING_MODE = True
settings.MONGODB_URL = "mongodb://localhost:27017"
settings.DATABASE_NAME = "test_casino_db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database for integration tests"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    test_db = client[settings.DATABASE_NAME]
    
    # Create indexes
    await test_db.users.create_index("_id")
    await test_db.transactions.create_index("_id")
    await test_db.transactions.create_index("user_id")
    
    yield test_db
    
    # Cleanup after all tests
    await test_db.transactions.delete_many({})
    await test_db.users.delete_many({})
    client.close()

@pytest.fixture
async def client(test_db):
    """Override database dependency for test client"""
    async def override_get_database():
        return test_db
    
    app.dependency_overrides[get_database] = override_get_database
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
async def mock_payment_provider():
    """Mock payment provider for testing"""
    provider = MagicMock(spec=PaymentProvider)
    provider.create_payment_order = AsyncMock(
        return_value={
            "order_id": "mock_order_123",
            "payment_url": "https://mock.ccpayment.com/pay",
            "crypto_address": "TQw4omxNEfqxmAqATqVfPGJBgLKhVDXTB1"
        }
    )
    provider.create_withdrawal = AsyncMock(
        return_value={
            "withdraw_id": "mock_withdraw_123",
            "status": "success"
        }
    )
    provider.verify_webhook_signature = MagicMock(return_value=True)
    return provider

@pytest.fixture
async def test_user(test_db):
    """Create test user with balance"""
    user_id = 123456789  # Use telegram_id as _id
    await test_db.users.delete_one({"_id": user_id})
    await test_db.users.insert_one({
        "_id": user_id,
        "telegram_id": user_id,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "balance": 1000.0,
        "is_active": True,
        "is_premium": False
    })
    yield user_id
    await test_db.users.delete_one({"_id": user_id})

@pytest.fixture
async def authenticated_client(client: AsyncClient, test_user):
    """Create authenticated client with test user token"""
    # Login to get token
    response = await client.post(
        "/api/auth/login",
        json={"init_data": str(test_user)}
    )
    
    assert response.status_code == 200
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Create new client with auth header
    async with AsyncClient(
        app=app, 
        base_url="http://test",
        headers={"Authorization": f"Bearer {access_token}"}
    ) as ac:
        yield ac
