import hashlib
import hmac
import time
from typing import Dict, Any, Protocol
import httpx
import traceback
from fastapi import HTTPException
from app.config import get_settings

settings = get_settings()

class PaymentProvider(Protocol):
    """Interface for payment providers"""
    async def create_payment_order(self, order_id: str, amount: float, 
                                   currency: str, **kwargs) -> Dict[str, Any]: ...
    async def create_withdrawal(self, withdraw_id: str, wallet_address: str,
                               amount: float, currency: str, **kwargs) -> Dict[str, Any]: ...
    def verify_webhook_signature(self, timestamp: str, sign: str, 
                                data: Dict[str, Any]) -> bool: ...

class CCPaymentClient:
    def __init__(self):
        self.app_id = settings.CCPAYMENT_APP_ID
        self.app_secret = settings.CCPAYMENT_APP_SECRET
        self.base_url = settings.CCPAYMENT_API_URL
        
        # Configure proxy if available (QuotaGuard Static)
        proxies = None
        if settings.QUOTAGUARDSTATIC_URL:
            proxies = {
                "http://": settings.QUOTAGUARDSTATIC_URL,
                "https://": settings.QUOTAGUARDSTATIC_URL
            }
            print("🔒 CCPayment Service: Using Static IP Proxy")
            
        self.client = httpx.AsyncClient(timeout=30.0, proxies=proxies)
    
    def _generate_signature(self, timestamp: str, data: Dict[str, Any]) -> str:
        sorted_params = sorted(data.items())
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params if v is not None])
        sign_str = f"{sign_str}&timestamp={timestamp}"
        
        signature = hmac.new(
            self.app_secret.encode(),
            sign_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature

    def _generate_v2_signature(self, timestamp: str, body_str: str) -> str:
        """
        V2 Signature: SHA256(AppID + AppSecret + Timestamp + Body)
        """
        # Concatenate: AppID + AppSecret + Timestamp + Body
        raw_str = f"{self.app_id}{self.app_secret}{timestamp}{body_str}"
        print(f"DEBUG SIGNATURE INPUT: {raw_str}")
        
        # SHA256 Hash
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
    
    def verify_webhook_signature(self, timestamp: str, sign: str, data: Dict[str, Any]) -> bool:
        """Verify webhook signature from CCPayment"""
        try:
            expected_signature = self._generate_signature(timestamp, data)
            return hmac.compare_digest(sign, expected_signature)
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    async def create_payment_order(
        self,
        order_id: str,
        amount: float,
        currency: str,
        product_name: str = "Casino Deposit",
        notify_url: str = None,
        return_url: str = None
    ) -> Dict[str, Any]:
        try:
            # V2 Timestamp: Seconds (10 digits)
            timestamp = str(int(time.time()))
            
            # V2 Payload
            payload = {
                "orderId": order_id,
                "price": str(amount),
                "product": product_name,
                "expiredAt": int(time.time()) + 3600, # 1 hour validity
                "fiatId": 1033 # USD
                # "appId": self.app_id # Standard docs say header only
            }
            
            if notify_url:
                payload["notifyUrl"] = notify_url
            if return_url:
                payload["returnUrl"] = return_url
            
            import json
            # Using standard JSON (with spaces) as per debug logs
            body_str = json.dumps(payload) 
            
            # Helper to strip secret just in case
            safe_secret = self.app_secret.strip()
            
            # Generate Signature
            # Concatenate: AppID + AppSecret + Timestamp + Body
            raw_str = f"{self.app_id}{safe_secret}{timestamp}{body_str}"
            
            print(f"DEBUG DETAILS: AppID={self.app_id} | SecretLen={len(safe_secret)} | Time={timestamp}")
            print(f"DEBUG BODY: {body_str}")
            print(f"DEBUG SIGNATURE INPUT: {raw_str}")
            
            signature = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
            
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Appid": self.app_id, 
                "Timestamp": timestamp,
                "Sign": signature
            }
            
            # Use User-Provided URL (ccpayment.com) because admin.ccpayment.com returned 404
            full_url = "https://ccpayment.com/ccpayment/v2/createInvoiceUrl"
             
            response = await self.client.post(
                full_url,
                content=body_str,
                headers=headers
            )
            
            try:
                result = response.json()
            except ValueError as e:
                print(f"❌ CCPayment JSON Error. Status: {response.status_code}, Raw response: '{response.text}'")
                raise HTTPException(status_code=502, detail=f"Invalid response from payment provider: {response.text[:200]}")
            
            if result.get("code") != 10000:
                print(f"❌ CCPayment API Error: {result}")
                raise HTTPException(
                    status_code=400,
                    detail=f"CCPayment API error: {result.get('msg', 'Unknown error')}"
                )
            
            return result.get("data", {})
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"CCPayment Service Init Error: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"CCPayment Service Init Error: {str(e)}")
    
    async def create_withdrawal(
        self,
        withdraw_id: str,
        wallet_address: str,
        amount: float,
        currency: str,
        notify_url: str = None
    ) -> Dict[str, Any]:
        timestamp = str(int(time.time() * 1000))
        
        payload = {
            "app_id": self.app_id,
            "merchant_order_id": withdraw_id,
            "withdraw_address": wallet_address,
            "withdraw_amount": str(amount),
            "withdraw_currency": currency,
        }
        
        if notify_url:
            payload["notify_url"] = notify_url
        
        signature = self._generate_signature(timestamp, payload)
        
        headers = {
            "Content-Type": "application/json",
            "Appid": self.app_id,
            "Timestamp": timestamp,
            "Sign": signature
        }
        
        response = await self.client.post(
            f"{self.base_url}/withdraw/create",
            json=payload,
            headers=headers
        )
        
        result = response.json()
        
        if result.get("code") != 10000:
            raise HTTPException(
                status_code=400,
                detail=f"CCPayment API error: {result.get('msg', 'Unknown error')}"
            )
        
        return result.get("data", {})
    
    def verify_webhook_signature(self, timestamp: str, sign: str, data: Dict[str, Any]) -> bool:
        expected_sign = self._generate_signature(timestamp, data)
        return hmac.compare_digest(expected_sign, sign)

# Mock implementation for testing
class MockPaymentProvider:
    """Mock payment provider for testing without real API credentials"""
    
    async def create_payment_order(
        self,
        order_id: str,
        amount: float,
        currency: str,
        **kwargs
    ) -> Dict[str, Any]:
        return {
            "order_id": f"mock_{order_id}",
            "payment_url": f"https://mock-payment.com/pay/{order_id}",
            "crypto_address": "TMockAddress123456789",
            "amount": str(amount),
            "currency": currency
        }
    
    async def create_withdrawal(
        self,
        withdraw_id: str,
        wallet_address: str,
        amount: float,
        currency: str,
        **kwargs
    ) -> Dict[str, Any]:
        return {
            "withdraw_id": f"mock_{withdraw_id}",
            "status": "processing",
            "amount": str(amount),
            "currency": currency
        }
    
    def verify_webhook_signature(self, timestamp: str, sign: str, data: Dict[str, Any]) -> bool:
        # In testing mode, always return True
        return True

def get_payment_provider() -> PaymentProvider:
    """Factory function to get the appropriate payment provider"""
    if settings.TESTING_MODE:
        return MockPaymentProvider()
    return CCPaymentClient()