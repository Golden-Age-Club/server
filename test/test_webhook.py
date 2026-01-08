import pytest
from httpx import AsyncClient
from datetime import datetime

@pytest.mark.asyncio
async def test_webhook_deposit_success(client: AsyncClient, test_user, test_db):
    # Create a deposit first
    deposit_response = await client.post(
        "/api/wallet/deposit",
        json={
            "user_id": test_user,
            "amount": 100.0,
            "currency": "USDT.TRC20"
        }
    )
    
    # Get the merchant order ID
    transaction_id = deposit_response.json()["transaction_id"]
    transaction = await test_db.transactions.find_one({"_id": transaction_id})
    merchant_order_id = transaction["merchant_order_id"]
    
    # Initial balance
    initial_balance = await test_db.users.find_one({"_id": test_user})
    initial_balance = initial_balance["balance"]
    
    # Simulate webhook from CCPayment
    webhook_payload = {
        "merchant_order_id": merchant_order_id,
        "order_status": "paid",
        "amount": "100.0",
        "currency": "USDT.TRC20"
    }
    
    response = await client.post(
        "/api/webhook/ccpayment",
        json=webhook_payload,
        headers={
            "timestamp": str(int(datetime.now().timestamp() * 1000)),
            "sign": "mock_signature"
        }
    )
    
    assert response.status_code == 200
    
    # Check balance was updated
    updated_user = await test_db.users.find_one({"_id": test_user})
    assert updated_user["balance"] == initial_balance + 100.0
    
    # Check transaction status
    updated_transaction = await test_db.transactions.find_one({"_id": transaction_id})
    assert updated_transaction["status"] == "completed"

@pytest.mark.asyncio
async def test_webhook_withdrawal_failed_refund(client: AsyncClient, test_user, test_db):
    # Create a withdrawal first
    withdrawal_response = await client.post(
        "/api/wallet/withdraw",
        json={
            "user_id": test_user,
            "amount": 50.0,
            "wallet_address": "TTestAddress123",
            "currency": "USDT.TRC20"
        }
    )
    
    transaction_id = withdrawal_response.json()["transaction_id"]
    transaction = await test_db.transactions.find_one({"_id": transaction_id})
    merchant_order_id = transaction["merchant_order_id"]
    
    # Get balance after withdrawal
    user = await test_db.users.find_one({"_id": test_user})
    balance_after_withdrawal = user["balance"]
    
    # Simulate failed withdrawal webhook
    webhook_payload = {
        "merchant_order_id": merchant_order_id,
        "order_status": "failed",
        "amount": "50.0",
        "currency": "USDT.TRC20"
    }
    
    response = await client.post(
        "/api/webhook/ccpayment",
        json=webhook_payload,
        headers={
            "timestamp": str(int(datetime.now().timestamp() * 1000)),
            "sign": "mock_signature"
        }
    )
    
    assert response.status_code == 200
    
    # Check balance was refunded
    updated_user = await test_db.users.find_one({"_id": test_user})
    assert updated_user["balance"] == balance_after_withdrawal + 50.0