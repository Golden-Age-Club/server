#!/usr/bin/env python3
import os
import sys

def check_env():
    """
    Check for critical environment variables before application start.
    """
    required_vars = [
        "MONGODB_URL",
        "JWT_SECRET_KEY",
        "ADMIN_WS_SECRET",
    ]
    
    missing = []
    
    print("Locked & Loaded: Checking Environment...")
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        elif var == "JWT_SECRET_KEY" and len(value) < 16:
             print(f"⚠️  WARNING: {var} is too short! Recommended 32+ chars.")
             
    if missing:
        print("\n❌ CRITICAL: Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nThe application cannot start securely. Please set these variables.")
        sys.exit(1)
        
    print("✅ Environment Check Passed.")

if __name__ == "__main__":
    check_env()
