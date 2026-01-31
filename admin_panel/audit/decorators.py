import functools
import json
from django.http import HttpRequest
from .models import AdminAuditLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(action_type, collection_name):
    """
    Decorator to log admin actions.
    Supports both Function-Based Views (request, ...) and Class-Based View methods (self, request, ...).
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            # Determine if called with (self, request) or (request)
            request = None
            if args:
                if isinstance(args[0], HttpRequest):
                    request = args[0]
                elif len(args) > 1 and isinstance(args[1], HttpRequest):
                     # Likely method call: self, request
                    request = args[1]
                elif hasattr(args[0], 'request'):
                     # View instance with attached request (e.g. form_valid(self, form))
                    request = args[0].request

            if not request:
                # Fallback or error, just execute without log
                return view_func(*args, **kwargs)

            # Execution
            response = view_func(*args, **kwargs)

            # Log Logic
            if 200 <= response.status_code < 400:
                try:
                    # Get target ID from kwargs (URL params usually)
                    # Note: in CBV, kwargs might be on self.kwargs if not passed to method
                    # But view_func methods usually don't get url params as kwargs unless dispatch
                    
                    target_id = kwargs.get('pk') or kwargs.get('id') or kwargs.get('user_id')
                    
                    # If target_id is missing, try to find it in view instance attributes if CBV
                    if not target_id and hasattr(args[0], 'kwargs'):
                         view_instance = args[0]
                         target_id = view_instance.kwargs.get('pk') or view_instance.kwargs.get('id') or view_instance.kwargs.get('user_id')

                    # Capture changes
                    changes = None
                    if request.method == 'POST':
                        changes = dict(request.POST)
                        if 'csrfmiddlewaretoken' in changes:
                            del changes['csrfmiddlewaretoken']

                    AdminAuditLog.objects.create(
                        admin_user=request.user,
                        action_type=action_type,
                        target_collection=collection_name,
                        target_id=str(target_id) if target_id else "N/A",
                        changes=changes,
                        ip_address=get_client_ip(request),
                        details=f"View: {view_func.__name__}"
                    )
                except Exception as e:
                    print(f"Failed to create audit log: {e}")
            
            return response
        return wrapper
    return decorator
