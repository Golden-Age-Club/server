from django.db import models
from django.conf import settings

class AdminAuditLog(models.Model):
    ACTION_TYPES = (
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('DISABLE', 'Disable'),
        ('ENABLE', 'Enable'),
    )

    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action_time = models.DateTimeField(auto_now_add=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_collection = models.CharField(max_length=50) # users, transactions
    target_id = models.CharField(max_length=100)
    changes = models.JSONField(blank=True, null=True) # Snapshot of changes
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-action_time']

    def __str__(self):
        return f"{self.admin_user} - {self.action_type} - {self.target_collection}/{self.target_id}"
