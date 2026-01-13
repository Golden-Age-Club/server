import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.join(os.path.dirname(__file__), '../admin_panel'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    email = "admin@goldenage.com"
    password = "adminpassword123"
    
    if not User.objects.filter(username="admin").exists():
        print("Creating superuser 'admin'...")
        User.objects.create_superuser("admin", email, password)
        print("✅ Superuser created successfully.")
        print(f"Login: {email} / admin (or username 'admin')")
        print(f"Password: {password}")
    else:
        print("⚠️ Superuser 'admin' already exists.")

if __name__ == "__main__":
    create_admin()
