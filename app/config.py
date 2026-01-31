"""Application configuration management using Pydantic Settings."""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with type validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "Slot Machine Admin Backend"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1/admin"
    cors_origins: str = "http://localhost:3000"

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017/?replicaSet=rs0"
    mongodb_db_name: str = "slot_admin"
    mongodb_min_pool_size: int = 10
    mongodb_max_pool_size: int = 100

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_session_db: int = 0
    redis_cache_db: int = 1
    redis_rate_limit_db: int = 2

    # Security
    secret_key: str = Field(..., min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Password Hashing
    bcrypt_rounds: int = 12

    # MFA
    mfa_issuer_name: str = "Slot Admin"
    mfa_digits: int = 6
    mfa_interval: int = 30

    # Rate Limiting
    rate_limit_login_attempts: int = 5
    rate_limit_login_window_minutes: int = 15
    rate_limit_api_requests: int = 100
    rate_limit_api_window_minutes: int = 1

    # Session
    session_expire_minutes: int = 480  # 8 hours
    session_inactivity_minutes: int = 15

    # Audit Logs
    audit_log_retention_days: int = 2555  # 7 years
    audit_log_mask_sensitive: bool = True

    # IP Whitelisting
    ip_whitelist: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Initial Super Admin
    initial_admin_username: str = "superadmin"
    initial_admin_email: str = "admin@slotadmin.com"
    initial_admin_password: str = "ChangeMe123!"

    @property
    def cors_origins_list(self) -> List[str]:
        """Get parsed CORS origins list."""
        if not self.cors_origins:
            return []
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def ip_whitelist_list(self) -> List[str]:
        """Get IP whitelist as list."""
        if not self.ip_whitelist:
            return []
        return [ip.strip() for ip in self.ip_whitelist.split(",")]


# Global settings instance
settings = Settings()
