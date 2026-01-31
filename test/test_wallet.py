import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_deposit(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/api/wallet/deposit",
        json={
            "amount": 100.0,
            "currency": "USDT.TRC20"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["amount"] == 100.0
    assert data["type"] == "deposit"
    assert data["status"] == "pending"
    assert "payment_url" in data
    assert "payment_address" in data

@pytest.mark.asyncio
async def test_create_withdrawal_success(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/api/wallet/withdraw",
        json={
            "amount": 50.0,
            "wallet_address": "TTestWalletAddress123",
            "currency": "USDT.TRC20"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["amount"] == 50.0
    assert data["type"] == "withdrawal"
    assert data["status"] == "processing"

@pytest.mark.asyncio
async def test_create_withdrawal_insufficient_balance(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/api/wallet/withdraw",
        json={
            "amount": 5000.0,  # More than available
            "wallet_address": "TTestWalletAddress123",
            "currency": "USDT.TRC20"
        }
    )
    
    assert response.status_code == 400
    assert "Insufficient balance" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_balance(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/wallet/balance")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "balance" in data
    assert data["balance"] == 1000.0

@pytest.mark.asyncio
async def test_get_transactions(authenticated_client: AsyncClient):
    # First create a transaction
    await authenticated_client.post(
        "/api/wallet/deposit",
        json={
            "amount": 100.0,
            "currency": "USDT.TRC20"
        }
    )
    
    # Then get transactions
    response = await authenticated_client.get("/api/wallet/transactions")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "transactions" in data
    assert len(data["transactions"]) > 0

@pytest.mark.asyncio
async def test_unauthorized_wallet_access(client: AsyncClient):
    """Test that wallet endpoints require authentication"""
    response = await client.get("/api/wallet/balance")
    
    assert response.status_code == 401
