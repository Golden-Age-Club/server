import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_creates_new_user(client: AsyncClient, test_db):
    """Test that login creates a new user if doesn't exist"""
    telegram_id = 999888777
    
    response = await client.post(
        "/api/auth/login",
        json={"init_data": str(telegram_id)}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["telegram_id"] == telegram_id
    assert data["user"]["balance"] == 0.0
    
    # Cleanup
    await test_db.users.delete_one({"_id": telegram_id})


@pytest.mark.asyncio
async def test_login_existing_user(client: AsyncClient, test_user, test_db):
    """Test login with existing user"""
    response = await client.post(
        "/api/auth/login",
        json={"init_data": str(test_user)}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["user"]["telegram_id"] == test_user
    assert data["user"]["balance"] == 1000.0


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, authenticated_client):
    """Test getting current user profile"""
    response = await authenticated_client.get("/api/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "telegram_id" in data
    assert "balance" in data


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, authenticated_client):
    """Test refreshing access token"""
    response = await authenticated_client.post("/api/auth/refresh")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test that endpoints require authentication"""
    # Try to access protected endpoint without auth
    response = await client.get("/api/auth/me")
    
    assert response.status_code == 401
