"""Authentication service - business logic for login, MFA, sessions."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as redis

from app.config import settings
from app.core.security import (
    verify_password, hash_password, create_access_token, create_refresh_token,
    decode_token, hash_token, generate_mfa_secret, get_totp_uri, 
    generate_qr_code, verify_totp, generate_session_id
)
from app.core.exceptions import (
    AuthenticationError, AccountLockedError, MFARequiredError
)
from app.models.admin import AdminUser
from app.models.session import AdminSession


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: AsyncIOMotorDatabase, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
    
    async def authenticate_admin(self, username: str, password: str) -> AdminUser:
        """Authenticate admin user with username and password."""
        
        # Find admin by username
        admin_doc = await self.db.admin_users.find_one({"username": username})
        
        if not admin_doc:
            # Increment failed attempts for IP tracking (prevent user enumeration)
            raise AuthenticationError("Invalid credentials")
        
        admin = AdminUser(**admin_doc)
        
        # Check if account is locked
        if admin.locked_until and admin.locked_until > datetime.utcnow():
            raise AccountLockedError(
                f"Account locked until {admin.locked_until.isoformat()}",
                details={"locked_until": admin.locked_until.isoformat()}
            )
        
        # Check if account is active
        if admin.status != "active":
            raise AuthenticationError(f"Account is {admin.status}")
        
        # Verify password
        if not verify_password(password, admin.password_hash):
            # Increment failed login attempts
            await self._increment_failed_attempts(admin.admin_id)
            raise AuthenticationError("Invalid credentials")
        
        # Reset failed attempts on successful login
        await self._reset_failed_attempts(admin.admin_id)
        
        # Update last login
        await self.db.admin_users.update_one(
            {"admin_id": admin.admin_id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return admin
    
    async def create_session(
        self,
        admin: AdminUser,
        ip_address: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """Create a new session with access and refresh tokens."""
        
        session_id = generate_session_id()
        
        # Create tokens
        token_data = {
            "sub": admin.admin_id,
            "username": admin.username,
            "roles": admin.roles,
            "session_id": session_id
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Create session object
        expires_at = datetime.utcnow() + timedelta(minutes=settings.session_expire_minutes)
        
        session = AdminSession(
            session_id=session_id,
            admin_id=admin.admin_id,
            access_token_hash=hash_token(access_token),
            refresh_token_hash=hash_token(refresh_token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        # Store session in Redis
        session_key = f"session:{session_id}"
        await self.redis.setex(
            session_key,
            settings.session_expire_minutes * 60,
            session.model_dump_json()
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "session_id": session_id,
            "mfa_required": admin.mfa_enabled
        }
    
    async def refresh_session(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token."""
        
        # Decode refresh token
        payload = decode_token(refresh_token)
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        # Get session ID and admin ID
        session_id = payload.get("session_id")
        admin_id = payload.get("sub")
        
        if not session_id or not admin_id:
            raise AuthenticationError("Invalid token payload")
        
        # Verify session exists
        session_key = f"session:{session_id}"
        session_data = await self.redis.get(session_key)
        
        if not session_data:
            raise AuthenticationError("Session expired or invalid")
        
        # Verify refresh token hash matches
        session = AdminSession.model_validate_json(session_data)
        if session.refresh_token_hash != hash_token(refresh_token):
            raise AuthenticationError("Invalid refresh token")
        
        # Get admin user
        admin_doc = await self.db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc or admin_doc.get("status") != "active":
            raise AuthenticationError("Admin account not found or inactive")
        
        admin = AdminUser(**admin_doc)
        
        # Create new tokens (refresh token rotation)
        token_data = {
            "sub": admin.admin_id,
            "username": admin.username,
            "roles": admin.roles,
            "session_id": session_id
        }
        
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        # Update session with new token hashes
        session.access_token_hash = hash_token(new_access_token)
        session.refresh_token_hash = hash_token(new_refresh_token)
        session.last_activity = datetime.utcnow()
        
        # Update in Redis
        await self.redis.setex(
            session_key,
            settings.session_expire_minutes * 60,
            session.model_dump_json()
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    
    async def logout(self, session_id: str):
        """Invalidate a session."""
        session_key = f"session:{session_id}"
        await self.redis.delete(session_key)
    
    async def setup_mfa(self, admin_id: str) -> Dict[str, str]:
        """Generate MFA secret and QR code for admin."""
        
        admin_doc = await self.db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc:
            raise AuthenticationError("Admin not found")
        
        admin = AdminUser(**admin_doc)
        
        # Generate new MFA secret
        secret = generate_mfa_secret()
        
        # Get provisioning URI
        provisioning_uri = get_totp_uri(secret, admin.username)
        
        # Generate QR code
        qr_code = generate_qr_code(provisioning_uri)
        
        # Store secret (not enabled yet)
        await self.db.admin_users.update_one(
            {"admin_id": admin_id},
            {"$set": {"mfa_secret": secret}}
        )
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "provisioning_uri": provisioning_uri
        }
    
    async def enable_mfa(self, admin_id: str, code: str) -> bool:
        """Enable MFA after verifying the first code."""
        
        admin_doc = await self.db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc:
            raise AuthenticationError("Admin not found")
        
        admin = AdminUser(**admin_doc)
        
        if not admin.mfa_secret:
            raise AuthenticationError("MFA not set up. Call setup_mfa first.")
        
        # Verify code
        if not verify_totp(admin.mfa_secret, code):
            raise AuthenticationError("Invalid MFA code")
        
        # Enable MFA
        await self.db.admin_users.update_one(
            {"admin_id": admin_id},
            {"$set": {"mfa_enabled": True}}
        )
        
        return True
    
    async def verify_mfa(self, admin_id: str, code: str) -> bool:
        """Verify MFA code."""
        
        admin_doc = await self.db.admin_users.find_one({"admin_id": admin_id})
        if not admin_doc:
            raise AuthenticationError("Admin not found")
        
        admin = AdminUser(**admin_doc)
        
        if not admin.mfa_enabled or not admin.mfa_secret:
            raise AuthenticationError("MFA not enabled")
        
        return verify_totp(admin.mfa_secret, code)
    
    async def _increment_failed_attempts(self, admin_id: str):
        """Increment failed login attempts and lock account if threshold exceeded."""
        
        result = await self.db.admin_users.find_one_and_update(
            {"admin_id": admin_id},
            {"$inc": {"failed_login_attempts": 1}},
            return_document=True
        )
        
        if result and result.get("failed_login_attempts", 0) >= 5:
            # Lock account for 15 minutes
            locked_until = datetime.utcnow() + timedelta(minutes=15)
            await self.db.admin_users.update_one(
                {"admin_id": admin_id},
                {
                    "$set": {"locked_until": locked_until},
                    "$set": {"failed_login_attempts": 0}
                }
            )
    
    async def _reset_failed_attempts(self, admin_id: str):
        """Reset failed login attempts."""
        await self.db.admin_users.update_one(
            {"admin_id": admin_id},
            {
                "$set": {
                    "failed_login_attempts": 0,
                    "locked_until": None
                }
            }
        )
