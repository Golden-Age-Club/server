import time
import hmac
import hashlib
import urllib.parse
import json
from typing import Dict, Any, Protocol, Optional

import httpx
from fastapi import HTTPException

from app.config import get_settings


settings = get_settings()


class CasinoGameProvider(Protocol):
    async def get_options(self) -> Dict[str, Any]:
        ...
    async def get_games(self) -> Dict[str, Any]:
        ...
    async def launch_game(
        self,
        game_id: int,
        player_id: str,
        player_token: str,
        language: str = "en",
        currency: str = "USD",
        exit_url: Optional[str] = None,
        base_url: Optional[str] = None,
        wallet_url: Optional[str] = None,
        other_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        ...


class PGProviderClient:
    def __init__(self) -> None:
        self.app_id = settings.PG_APP_ID
        self.api_key = settings.PG_API_KEY
        self.base_url = settings.PG_API_BASE_URL.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)

    def _create_sign(self, request_time: str) -> str:
        raw = f"{self.app_id}{request_time}"
        encoded = urllib.parse.quote(raw, safe="")
        return hmac.new(
            self.api_key.encode("utf-8"),
            encoded.encode("utf-8"),
            hashlib.md5,
        ).hexdigest()

    def _create_play_sign(self, params: Dict[str, Any]) -> str:
        def serialize(value):
            if isinstance(value, (dict, list)):
                return json.dumps(value, separators=(',', ':'), ensure_ascii=False)
            return str(value)

        # Provider's steps: collect values (exclude sign/urls), comma-separate, URL-encode, HMAC-MD5
        values = [serialize(params[key]) for key in params if key not in ('sign', 'urls')]
        concatenated = "".join(values) # Updated to empty string join based on Node.js sample
        encoded = urllib.parse.quote(concatenated, safe='')
        return hmac.new(self.api_key.encode('utf-8'), encoded.encode('utf-8'), hashlib.md5).hexdigest()

    async def get_options(self) -> Dict[str, Any]:
        if not self.app_id or not self.api_key:
            raise HTTPException(status_code=500, detail="PG provider not configured")

        request_time = str(int(time.time() * 1000))
        sign = self._create_sign(request_time)

        params = {
            "app_id": self.app_id,
            "request_time": request_time,
            "sign": sign,
        }

        url = f"{self.base_url}/api/v1/get-options"

        response = await self.client.get(
            url,
            params=params,
            headers={"Accept": "application/json"},
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"PG API error: {exc.response.text}",
            ) from exc

        return response.json()

    async def update_webhook_url(self, webhook_url: str) -> Dict[str, Any]:
        if not self.app_id or not self.api_key:
            raise HTTPException(status_code=500, detail="PG provider not configured")

        request_time = str(int(time.time() * 1000))
        
        # Prepare params for signature
        # Order: app_id, request_time, webhook_url
        params = {
            "app_id": self.app_id,
            "request_time": request_time,
            "webhook_url": webhook_url
        }
        
        # Calculate signature: concatenate values, URL encode, HMAC-MD5
        concatenated = "".join([str(params[k]) for k in params])
        encoded = urllib.parse.quote(concatenated, safe="")
        sign = hmac.new(
            self.api_key.encode("utf-8"),
            encoded.encode("utf-8"),
            hashlib.md5,
        ).hexdigest()
        
        params["sign"] = sign
        
        url = f"{self.base_url}/api/v1/webhook-url-update"
        
        # The documentation says "Query Parameters" but it's a POST request.
        # We will pass them as query params as per the Python example (requests.post(url, params=params))
        response = await self.client.post(
            url,
            params=params,
            headers={"Accept": "application/json"},
        )
        
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"PG API error: {exc.response.text}",
            ) from exc
            
    async def get_games(self) -> Dict[str, Any]:
        if not self.app_id or not self.api_key:
            raise HTTPException(status_code=500, detail="PG provider not configured")

        request_time = str(int(time.time() * 1000))
        sign = self._create_sign(request_time)

        params = {
            "app_id": self.app_id,
            "request_time": request_time,
            "sign": sign,
        }

        url = f"{self.base_url}/api/v1/get-games"

        response = await self.client.get(
            url,
            params=params,
            headers={"Accept": "application/json"},
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"PG API error: {exc.response.text}",
            ) from exc

        return response.json()

    async def launch_game(
        self,
        game_id: int,
        player_id: str,
        player_token: str,
        language: str = "en",
        currency: str = "USD",
        exit_url: Optional[str] = None,
        base_url: Optional[str] = None,
        wallet_url: Optional[str] = None,
        other_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.app_id or not self.api_key:
            raise HTTPException(status_code=500, detail="PG provider not configured")

        request_time = int(time.time() * 1000)

        # Construct payload with specific order if possible, though Python dicts are insertion ordered.
        # Order based on user sample: exit, game_id, player_id, player_token, app_id, language, currency, request_time, urls
        payload = {}
        if exit_url:
            payload["exit"] = exit_url
        
        payload["game_id"] = game_id
        payload["player_id"] = player_id
        payload["player_token"] = player_token
        payload["app_id"] = self.app_id
        payload["language"] = language
        payload["currency"] = currency
        payload["request_time"] = request_time

        urls = {}
        if base_url:
            urls["base_url"] = base_url
        if wallet_url:
            urls["wallet_url"] = wallet_url
        if other_url:
            urls["other_url"] = other_url
        
        if urls:
            payload["urls"] = urls

        # Generate signature
        payload["sign"] = self._create_play_sign(payload)

        url = f"{self.base_url}/api/v1/playGame"

        response = await self.client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        print(response)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
             # Try to parse error response if available
            error_detail = exc.response.text
            try:
                error_json = exc.response.json()
                if "err_desc" in error_json:
                    error_detail = error_json["err_desc"]
            except Exception:
                pass
                
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"PG API error: {error_detail}",
            ) from exc
        print(response.json())
        return response.json()


class MockPGProvider:
    async def get_options(self) -> Dict[str, Any]:
        return {
            "provider": "PG",
            "app_name": settings.PG_APP_NAME,
            "mock": True,
            "categories": [],
        }

    async def get_games(self) -> Dict[str, Any]:
        return {
            "games": [
                {
                    "categories": ["51"],
                    "id": 4601,
                    "lower_key": "supertwister",
                    "game_type": 1,
                    "uniq_provider": "habanero",
                    "provider_title": "Habanero",
                    "name": "Super Twister",
                    "image": "https://mimgs.cdnparts.com/ts2/habanero/supertwister.jpg",
                    "provider_code": "HABANERO",
                    "provider_id": 1152,
                    "is_active": 1,
                    "background": "https://www.cmsbetconstruct.com/content/images/casino/background/ffe5ca058c9ca633f31a6627a34c5293_background.jpeg",
                    "sorder": 1000,
                }
            ]
        }

    async def launch_game(
        self,
        game_id: int,
        player_id: str,
        player_token: str,
        language: str = "en",
        currency: str = "USD",
        exit_url: Optional[str] = None,
        base_url: Optional[str] = None,
        wallet_url: Optional[str] = None,
        other_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "result": True,
            "err_code": 0,
            "err_desc": "",
            "url": f"https://mock-pg.com/gamestart?token={player_token}&game={game_id}"
        }


def get_pg_provider() -> CasinoGameProvider:
    if settings.TESTING_MODE:
        return MockPGProvider()
    return PGProviderClient()
