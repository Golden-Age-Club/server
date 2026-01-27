import logging
import uuid
from datetime import timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import BaseModel

from app.services.pg_provider import CasinoGameProvider, get_pg_provider
from app.middleware.auth import get_current_user, create_access_token
from app.config import get_settings


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/casino", tags=["casino"])
settings = get_settings()


class PlayGameRequest(BaseModel):
    game_id: int
    exit_url: Optional[str] = None


class UpdateWebhookRequest(BaseModel):
    webhook_url: Optional[str] = None


@router.post("/pg/webhook-update")
async def update_webhook_url(
    request: UpdateWebhookRequest,
    provider: CasinoGameProvider = Depends(get_pg_provider),
    # current_user: Dict[str, Any] = Depends(get_current_user) # Optionally require auth, but for now open for testing or use admin auth if available
):
    try:
        # If no URL provided, use the configured one
        webhook_url = request.webhook_url
        if not webhook_url:
            # Construct the unified callback URL
            # Note: User must ensure API_HOST/PORT is reachable from internet
            # For local testing, this might be ngrok URL
            base_url = settings.WEBHOOK_URL.rsplit("/api/webhook", 1)[0] # Extract base if possible, or use explicit setting
            # Or just assume WEBHOOK_URL points to something valid and we append the new path
            # But wait, WEBHOOK_URL in config is "http://localhost:8000/api/webhook/ccpayment"
            # We want "https://yourdomain.com/api/v1/callback/unified"
            
            # Use the provided one or fallback to a constructed one from settings
            # Ideally user provides it explicitly in the request body
            if not webhook_url:
                 raise HTTPException(status_code=400, detail="webhook_url is required")

        data = await provider.update_webhook_url(webhook_url)
        return data
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error updating webhook URL", exc_info=exc)
        raise HTTPException(status_code=502, detail="Failed to update webhook URL") from exc

@router.get("/pg/options")
async def get_pg_options(provider: CasinoGameProvider = Depends(get_pg_provider)):
    try:
        data = await provider.get_options()
        return data
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error fetching PG options", exc_info=exc)
        raise HTTPException(status_code=502, detail="Failed to fetch PG options") from exc


@router.get("/pg/games")
async def get_pg_games(
    provider: CasinoGameProvider = Depends(get_pg_provider),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    provider_id: Optional[str] = Query(None, description="Filter by provider"),
    search: Optional[str] = Query(None, description="Search term")
):
    try:
        data = await provider.get_games(page=page, limit=limit, provider_id=provider_id, search=search)
        return data
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error fetching PG games", exc_info=exc)
        raise HTTPException(status_code=502, detail="Failed to fetch PG games") from exc


@router.post("/pg/play")
async def play_game(
    request: PlayGameRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    provider: CasinoGameProvider = Depends(get_pg_provider)
):
    try:
        # Generate a unique player token for this session (valid for 12 hours)
        # Provider requires 8-12 hours validity
        token_data = {
            "sub": str(current_user["_id"]),
            "type": "game_session",
            "game_id": request.game_id
        }
        player_token = create_access_token(token_data, expires_delta=timedelta(hours=12))
        
        # Use user's ID as player_id
        player_id = str(current_user["_id"])
        
        # Use user's language or default to "en"
        language = current_user.get("language_code", "en")
        
        # Default currency (could be configured or from user wallet)
        currency = "USD"

        # URLs for game integration
        frontend_url = settings.FRONTEND_URL.rstrip("/")
        exit_url = request.exit_url or f"{frontend_url}/"
        base_url = f"{frontend_url}/start-game"
        wallet_url = f"{frontend_url}/wallet"
        
        data = await provider.launch_game(
            game_id=request.game_id,
            player_id=player_id,
            player_token=player_token,
            language=language,
            currency=currency,
            exit_url=exit_url,
            base_url=base_url,
            wallet_url=wallet_url
        )
        return data
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error launching game", exc_info=exc)
        raise HTTPException(status_code=502, detail="Failed to launch game") from exc
