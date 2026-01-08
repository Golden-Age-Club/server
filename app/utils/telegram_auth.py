import hashlib
import hmac
import time
from typing import Dict, Optional
from urllib.parse import parse_qsl
from fastapi import HTTPException

def validate_telegram_webapp_data(init_data: str, bot_token: str, max_age: int = 86400) -> Dict[str, str]:
    """
    Validate Telegram WebApp initData using HMAC-SHA256
    
    Args:
        init_data: The initData string from Telegram WebApp
        bot_token: Your Telegram bot token
        max_age: Maximum age of the data in seconds (default 24 hours)
    
    Returns:
        Dictionary containing validated user data
    
    Raises:
        HTTPException: If validation fails
    """
    try:
        # Parse the init_data string
        parsed_data = dict(parse_qsl(init_data))
        
        # Extract hash and other data
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            raise HTTPException(status_code=401, detail="Missing hash in initData")
        
        # Check data freshness
        auth_date = parsed_data.get('auth_date')
        if not auth_date:
            raise HTTPException(status_code=401, detail="Missing auth_date in initData")
        
        auth_timestamp = int(auth_date)
        current_timestamp = int(time.time())
        
        if current_timestamp - auth_timestamp > max_age:
            raise HTTPException(
                status_code=401, 
                detail=f"initData is too old. Max age: {max_age} seconds"
            )
        
        # Create data check string
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)
        
        # Calculate secret key
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        if not hmac.compare_digest(calculated_hash, received_hash):
            raise HTTPException(status_code=401, detail="Invalid initData hash")
        
        return parsed_data
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid initData format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def parse_telegram_user(validated_data: Dict[str, str]) -> Dict:
    """
    Parse Telegram user data from validated initData
    
    Args:
        validated_data: Dictionary from validate_telegram_webapp_data
    
    Returns:
        Dictionary with user information
    """
    import json
    
    user_data = {}
    
    # Parse user JSON if present
    if 'user' in validated_data:
        try:
            user_json = json.loads(validated_data['user'])
            user_data = {
                'telegram_id': user_json.get('id'),
                'username': user_json.get('username'),
                'first_name': user_json.get('first_name'),
                'last_name': user_json.get('last_name'),
                'language_code': user_json.get('language_code', 'en'),
                'is_premium': user_json.get('is_premium', False),
                'photo_url': user_json.get('photo_url')
            }
        except json.JSONDecodeError:
            raise HTTPException(status_code=401, detail="Invalid user data in initData")
    
    return user_data


def validate_and_parse_telegram_data(init_data: str, bot_token: str) -> Dict:
    """
    Convenience function to validate and parse Telegram data in one call
    
    Args:
        init_data: The initData string from Telegram WebApp
        bot_token: Your Telegram bot token
    
    Returns:
        Dictionary with parsed user information
    """
    validated_data = validate_telegram_webapp_data(init_data, bot_token)
    user_data = parse_telegram_user(validated_data)
    
    if not user_data.get('telegram_id'):
        raise HTTPException(status_code=401, detail="Missing telegram_id in user data")
    
    return user_data
