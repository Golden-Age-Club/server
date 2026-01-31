import asyncio
import requests
import json

# Configuration
API_URL = "http://127.0.0.1:8001/api/auth"

def register_email_user():
    import random
    import string
    
    # Generate random user
    rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    username = f"user_{rand_suffix}"
    email = f"{username}@example.com"
    password = "SecretPassword123!"
    first_name = f"TestUser_{rand_suffix}"
    last_name = "Demo"
    
    print(f"Auto-generating user...")
    print(f"Email: {email}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    
    payload = {
        "email": email,
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name
    }
    
    try:
        # Note: You need the FastAPI server running. 
        # If it's not running, this will fail.
        # Assuming the user might want to run this against the local backend.
        
        # Since I can't guarantee the FastAPI server is UP right now (only Admin Panel might be),
        # I will write this as a direct repository call script instead?
        # No, a request script is better to test the REAL route.
        # But wait, looking at the user context, 'admin_panel/manage.py' is open. 
        # The FastAPI app is likely in 'main.py' or similar in root.
        
        response = requests.post(f"{API_URL}/register/email", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            user = data['user']
            user_id = user.get('_id') or user.get('id')
            print(f"\n✅ Registration Successful!")
            print(f"User ID: {user_id}")
            print(f"Token: {data['access_token'][:20]}...")
            print(f"Balance: {user['balance']}")
        else:
            print(f"\n❌ Registration Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the FastAPI Backend is running on port 8000.")

if __name__ == "__main__":
    register_email_user()
