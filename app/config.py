from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # CCPayment
    CCPAYMENT_APP_ID: str = Field(default="test_app_id")
    CCPAYMENT_APP_SECRET: str = Field(default="test_secret")
    CCPAYMENT_API_URL: str = Field(default="https://admin.ccpayment.com/ccpayment/v2")
    
    # MongoDB
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    DATABASE_NAME: str = Field(default="casino_db")
    
    # Application
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    WEBHOOK_URL: str = Field(default="http://localhost:8000/api/webhook/ccpayment")
    
    # Testing
    TESTING_MODE: bool = Field(default=False)
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="test_bot_token")
    
    # JWT Authentication
    JWT_SECRET_KEY: str = Field(default="super_secret_jwt_key_change_in_production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)
    
    # CORS
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000,http://localhost:5173,https://pghome.co")
    
    # Authentication
    AUTH_EXPIRATION_SECONDS: int = Field(default=86400)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="console")  # 'json' for production, 'console' for development
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
