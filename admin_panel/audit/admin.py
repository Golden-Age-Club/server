from django.contrib import admin
from .models import AdminAuditLog

@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'admin_user', 'action_type', 'target_collection', 'target_id')
    list_filter = ('action_type', 'target_collection', 'action_time')
    search_fields = ('target_id', 'details', 'admin_user__username')
    readonly_fields = ('action_time', 'admin_user', 'action_type', 'target_collection', 'target_id', 'changes', 'ip_address', 'details')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
