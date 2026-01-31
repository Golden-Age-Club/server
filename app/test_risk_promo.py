import asyncio
import os
import sys
import json
from httpx import AsyncClient
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.getcwd())

async def test_risk_promotions():
    base_url = "http://localhost:8000/api/v1/admin"
    
    async with AsyncClient(base_url=base_url, timeout=30.0) as client:
        # 1. Login
        print("Logging in...")
        try:
            login_res = await client.post("/auth/login", json={
                "username": "superadmin",
                "password": "ChangeMe123!"
            })
            login_data = login_res.json()
            token = login_data["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
        except Exception as e:
            print(f"Login failed: {e}")
            if 'login_res' in locals(): print(f"Response: {login_res.text}")
            return
        
        # 2. Test Risk Rules
        print("\nFetching Risk Rules...")
        risk_res = await client.get("/risk/rules", headers=headers)
        risk_data = risk_res.json()
        if not risk_data.get("success"):
            print(f"Failed to fetch risk rules: {risk_data.get('error')}")
        else:
            rules = risk_data["data"]
            print(f"Found {len(rules)} risk rules")
            for r in rules:
                print(f"- {r['description']} (Active: {r['is_active']})")

        # 3. Test Promotions
        print("\nCreating a new Promotion...")
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        promo_data = {
            "promo_id": "welcome_2026",
            "name": "Welcome Bonus 2026",
            "description": "100% deposit match for new players",
            "type": "welcome",
            "bonus_percent": 100.0,
            "max_bonus": 500.0,
            "min_deposit": 10.0,
            "wagering_requirement": 35,
            "status": "active",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        promo_res = await client.post("/promotions/", headers=headers, json=promo_data)
        promo_result = promo_res.json()
        print(f"Promotion creation response: {promo_result.get('success')}")
        if not promo_result.get("success"):
            print(f"Error: {promo_result.get('error')}")

        # 4. List Promotions
        print("\nListing all Promotions...")
        list_res = await client.get("/promotions/", headers=headers)
        list_data = list_res.json()
        if list_data.get("success"):
            promos = list_data["data"]
            print(f"Found {len(promos)} promotions")
            for p in promos:
                print(f"- {p['name']} (Status: {p['status']})")
        else:
            print(f"Failed to list promotions: {list_data.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_risk_promotions())
