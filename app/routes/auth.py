from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import TelegramAuthRequest, UserResponse, AuthResponse, EmailLoginRequest, EmailRegisterRequest
from app.repositories.user import UserRepository
from app.dependencies import get_user_repo
from app.utils.telegram_auth import validate_and_parse_telegram_data
from app.middleware.auth import create_access_token, get_current_user
from app.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login/telegram", response_model=AuthResponse)
async def login_telegram(
    request: TelegramAuthRequest,
    user_repo: UserRepository = Depends(get_user_repo)
):
    """
    Authenticate user with Telegram WebApp initData
    """
    # ... logic for validation similar to before ...
    if settings.TESTING_MODE:
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
        user_data = validate_and_parse_telegram_data(request.init_data, settings.TELEGRAM_BOT_TOKEN)
    
    telegram_id = user_data.get("telegram_id")
    logger.info(f"Login attempt for telegram_id: {telegram_id}")
    
    user = await user_repo.get_by_telegram_id(telegram_id)
    
    if not user:
        logger.info(f"Creating new user: {telegram_id}")
        user_id = await user_repo.create_user(user_data)
        user = await user_repo.get_by_id(user_id)
    else:
        await user_repo.update_user_info(telegram_id, {
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "photo_url": user_data.get("photo_url"),
            "language_code": user_data.get("language_code", "en"),
            "is_premium": user_data.get("is_premium", False)
        })
        user = await user_repo.get_by_telegram_id(telegram_id)
    
    # Create access token with generic user_id
    user["_id"] = str(user["_id"])
    access_token = create_access_token({"user_id": user["_id"], "telegram_id": user.get("telegram_id")})
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/register/email", response_model=AuthResponse)
async def register_email(
    request: EmailRegisterRequest,
    user_repo: UserRepository = Depends(get_user_repo)
):
    """Register new user with Email/Password"""
    from passlib.hash import bcrypt
    
    existing = await user_repo.get_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_data = {
        "email": request.email,
        "password_hash": bcrypt.hash(request.password),
        "first_name": request.first_name,
        "last_name": request.last_name
    }
    
    user_id = await user_repo.create_email_user(user_data)
    user = await user_repo.get_by_id(user_id)
    
    # Convert _id to string for Pydantic response
    user["_id"] = str(user["_id"])
    
    access_token = create_access_token({"user_id": user["_id"]})
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/login/email", response_model=AuthResponse)
async def login_email(
    request: EmailLoginRequest,
    user_repo: UserRepository = Depends(get_user_repo)
):
    """Login with Email/Password"""
    from passlib.hash import bcrypt
    
    user = await user_repo.get_by_email(request.email)
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not bcrypt.verify(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user["_id"] = str(user["_id"])
    access_token = create_access_token({"user_id": user["_id"]})
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/login", response_model=AuthResponse, deprecated=True)
async def login_legacy(
    request: TelegramAuthRequest,
    user_repo: UserRepository = Depends(get_user_repo)
):
    """Legacy endpoint alias for telegram login (Backward Compatibility)"""
    return await login_telegram(request, user_repo)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get current authenticated user's profile"""
    return current_user


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    current_user: dict = Depends(get_current_user)
):
    """Refresh access token"""
    access_token = create_access_token({
        "user_id": str(current_user["_id"]),
        "telegram_id": current_user.get("telegram_id")
    })
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=current_user
    )
