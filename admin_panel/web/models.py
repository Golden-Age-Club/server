from django.db import models

class Management(models.Model):
    """Dummy model to force the Web app to appear in Jazzmin sidebar"""
    class Meta:
        verbose_name_plural = "Management"
        managed = True  # Create a real table to avoid OperationalError
