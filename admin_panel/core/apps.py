from django.apps import AppConfig
import sys

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Prevent connection during migrations or management commands that don't need DB
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
            
        from .db import Database
        try:
            Database.connect()
        except Exception:
            pass # Handle gracefully if DB is down during startup check
