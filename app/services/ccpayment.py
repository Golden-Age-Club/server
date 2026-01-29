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
            timestamp = str(int(time.time() * 1000))
            
            # Using Hosted Checkout Page Integration endpoint
            # https://admin.ccpayment.com/ccpayment/v1/concise/url/get
            
            payload = {
                "app_id": self.app_id,
                "merchant_order_id": order_id,
                "product_price": str(amount),
                "order_valid_period": 3600, # 1 hour validity
                "product_name": product_name,
                # "fiat_currency_id": "", # Optional if using crypto
                # "order_currency": currency, # Not needed for hosted page if letting user choose? 
                # Actually for hosted page v1/concise/url/get, we usually send price.
                # Let's verify if 'order_currency' is valid here.
                # Documentation says 'product_price' and 'order_valid_period'.
                # But to force a specific currency we might need another param or just pass it differently.
                # For now let's stick to the hosted page generic flow where user selects coin, 
                # OR if we want to force TRC20, we might need to check if we can pass it.
                # Re-reading docs: "order_currency" might be for non-hosted or different endpoint.
                # However, the user wants to deposit USDT.TRC20. 
                # If we use concise/url/get, it opens a page. 
                # Let's try to pass the amount and let user pick (or if we can pre-select).
            }
            
            # Note: For concise/url/get, documentation usually requires:
            # merchant_order_id, product_price, product_name, order_valid_period.
            
            if notify_url:
                payload["notify_url"] = notify_url
            if return_url:
                payload["return_url"] = return_url
            
            # For hosted page, we might redirect user to this URL
            
            signature = self._generate_signature(timestamp, payload)
            
            headers = {
                "Content-Type": "application/json",
                "Appid": self.app_id,
                "Timestamp": timestamp,
                "Sign": signature
            }
            
            # Correct Endpoint for Hosted Checkout
            # Base URL is https://admin.ccpayment.com/ccpayment/v2 in config, 
            # but this endpoint is v1 sometimes? 
            # Let's look at the config. api_url is .../v2.
            # We need to be careful with the path.
            # If config is .../v2, we might need to replace it or just append if it was just host.
            # Config: https://admin.ccpayment.com/ccpayment/v2
            # We want: https://admin.ccpayment.com/ccpayment/v1/concise/url/get
            
            # Let's construct URL safely.
            base_url = self.base_url.replace("/v2", "/v1") # Hack due to config being fixed to v2
            
            response = await self.client.post(
                f"{base_url}/concise/url/get",
                json=payload,
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