import os
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # CCPayment
    CCPAYMENT_APP_ID: str = Field(default="test_app_id")
    CCPAYMENT_APP_SECRET: str = Field(min_length=1)  # Required in Prod
    CCPAYMENT_API_URL: str = Field(default="https://admin.ccpayment.com/ccpayment/v2")
    
    # Casino games provider (PG)
    PG_APP_NAME: str = Field(default="Golden Age Club")
    PG_APP_ID: str = Field(default="test_pg_app_id")
    PG_API_KEY: str = Field(default="test_pg_api_key")
    PG_API_BASE_URL: str = Field(default="https://mgc-example.com")
    
    # MongoDB
    MONGODB_URL: str = Field(min_length=1)  # Required in Prod
    DATABASE_NAME: str = Field(default="casino_db")
    
    # Application
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = int(os.environ.get("PORT", 8000))
    WEBHOOK_URL: str = Field(default="http://localhost:8000/api/webhook/ccpayment")
    
    # Testing
    TESTING_MODE: bool = Field(default=False)
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="test_bot_token")
    
    # JWT Authentication
    JWT_SECRET_KEY: str = Field(min_length=32)  # Required in Prod, must be strong
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)
    
    # CORS
    # In Prod, this should include the Admin Panel URL
    ALLOWED_ORIGINS: str = Field(default="http://localhost:5173,https://pghome.co")
    
    # Frontend
    FRONTEND_URL: str = Field(default="http://localhost:5173")
    
    # Authentication
    AUTH_EXPIRATION_SECONDS: int = Field(default=86400)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="console")  # 'json' for production, 'console' for development
    
    # Support System
    ADMIN_WS_SECRET: str = Field(default="admin_secret_key_123", min_length=8) # Required in Prod
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
