"""Security utilities: password hashing, JWT, MFA."""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import pyotp
import qrcode
import io
import base64

from jose import JWTError, jwt

from app.config import settings
from app.core.exceptions import AuthenticationError


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique token ID for rotation
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def hash_token(token: str) -> str:
    """Create a hash of a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_mfa_secret() -> str:
    """Generate a new MFA secret for TOTP."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, username: str) -> str:
    """Get TOTP provisioning URI for QR code generation."""
    totp = pyotp.TOTP(
        secret,
        digits=settings.mfa_digits,
        interval=settings.mfa_interval
    )
    return totp.provisioning_uri(
        name=username,
        issuer_name=settings.mfa_issuer_name
    )


def generate_qr_code(data: str) -> str:
    """Generate QR code as base64 encoded image."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code."""
    totp = pyotp.TOTP(
        secret,
        digits=settings.mfa_digits,
        interval=settings.mfa_interval
    )
    return totp.verify(code, valid_window=1)  # Allow 1 interval before/after


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return secrets.token_urlsafe(32)


def generate_idempotency_key() -> str:
    """Generate a unique idempotency key."""
    return secrets.token_urlsafe(32)
