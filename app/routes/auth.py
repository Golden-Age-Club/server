from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import TelegramAuthRequest, UserResponse, AuthResponse
from app.repositories.user import UserRepository
from app.dependencies import get_user_repo
from app.utils.telegram_auth import validate_and_parse_telegram_data
from app.middleware.auth import create_access_token, get_current_user
from app.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=AuthResponse)
async def login(
    request: TelegramAuthRequest,
    user_repo: UserRepository = Depends(get_user_repo)
):
    """
    Authenticate user with Telegram WebApp initData
    Creates user if doesn't exist (auto-registration)
    Returns JWT access token
    """
    # Skip validation in testing mode
    if settings.TESTING_MODE:
        # In testing mode, expect a simple telegram_id in init_data
        try:
            telegram_id = int(request.init_data)
            user_data = {
                "telegram_id": telegram_id,
                "username": f"test_user_{telegram_id}",
                "first_name": "Test",
                "last_name": "User"
            }
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid telegram_id in testing mode")
    else:
        # Validate Telegram initData
        user_data = validate_and_parse_telegram_data(request.init_data, settings.TELEGRAM_BOT_TOKEN)
    
    telegram_id = user_data.get("telegram_id")
    
    logger.info(f"Login attempt for telegram_id: {telegram_id}")
    
    # Check if user exists
    user = await user_repo.get_by_telegram_id(telegram_id)
    
    # Create user if doesn't exist (auto-registration)
    if not user:
        logger.info(f"Creating new user: {telegram_id}")
        await user_repo.create_user(user_data)
        user = await user_repo.get_by_telegram_id(telegram_id)
        logger.info(f"✅ New user created: {telegram_id}")
    else:
        # Update user info in case Telegram data changed
        logger.debug(f"Updating existing user info: {telegram_id}")
        update_data = {
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "photo_url": user_data.get("photo_url"),
            "language_code": user_data.get("language_code", "en"),
            "is_premium": user_data.get("is_premium", False)
        }
        await user_repo.update_user_info(telegram_id, update_data)
        user = await user_repo.get_by_telegram_id(telegram_id)
    
    # Create access token
    access_token = create_access_token({"telegram_id": telegram_id})
    logger.info(f"✅ Login successful for telegram_id: {telegram_id}")
    
    # Prepare user response
    user_response = UserResponse(
        telegram_id=user["telegram_id"],
        username=user.get("username"),
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        photo_url=user.get("photo_url"),
        language_code=user.get("language_code", "en"),
        balance=user.get("balance", 0.0),
        is_active=user.get("is_active", True),
        is_premium=user.get("is_premium", False),
        created_at=user["created_at"],
        updated_at=user["updated_at"]
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get current authenticated user's profile"""
    return UserResponse(
        telegram_id=current_user["telegram_id"],
        username=current_user.get("username"),
        first_name=current_user.get("first_name"),
        last_name=current_user.get("last_name"),
        photo_url=current_user.get("photo_url"),
        language_code=current_user.get("language_code", "en"),
        balance=current_user.get("balance", 0.0),
        is_active=current_user.get("is_active", True),
        is_premium=current_user.get("is_premium", False),
        created_at=current_user["created_at"],
        updated_at=current_user["updated_at"]
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    current_user: dict = Depends(get_current_user)
):
    """Refresh access token for authenticated user"""
    # Create new access token
    access_token = create_access_token({"telegram_id": current_user["telegram_id"]})
    
    user_response = UserResponse(
        telegram_id=current_user["telegram_id"],
        username=current_user.get("username"),
        first_name=current_user.get("first_name"),
        last_name=current_user.get("last_name"),
        photo_url=current_user.get("photo_url"),
        language_code=current_user.get("language_code", "en"),
        balance=current_user.get("balance", 0.0),
        is_active=current_user.get("is_active", True),
        is_premium=current_user.get("is_premium", False),
        created_at=current_user["created_at"],
        updated_at=current_user["updated_at"]
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )
