from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from repository.tickets import TicketRepository
from repository.support_messages import SupportMessageRepository
from django.conf import settings
import uuid

# Helper to check if user is admin
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class TicketListView(AdminRequiredMixin, TemplateView):
    template_name = 'web/support_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch open tickets from MongoDB repo
        context['tickets'] = TicketRepository.get_all_open()
        
        # Inject admin context for sidebar
        from django.contrib import admin
        context['app_label'] = 'web'
        context['model_name'] = 'support' # Mapped in settings to active link
        context.update(admin.site.each_context(self.request))
        return context

class TicketChatView(AdminRequiredMixin, TemplateView):
    template_name = 'web/support_chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_id = kwargs['ticket_id']
        context['ticket_id'] = ticket_id
        context['ticket'] = TicketRepository.get_by_id(ticket_id)
        context['messages'] = SupportMessageRepository.get_history(ticket_id)
        
        # In a real app, generate a short-lived JWT for the admin to use WS
        # For MVP, we'll use a mocked or static token if env allows, 
        # or implement a simple token generator in Django that FastAPI accepts.
        # For now, placeholder:
        import os
        context['admin_ws_token'] = os.getenv("ADMIN_WS_SECRET", "admin-bypass-token")
        
        # WEBSOCKET URL
        # Logic: If API_URL env var is set (Prod), use it. Else default to localhost.
        # This handles the split-server setup on Render.
        api_url = os.getenv('API_URL')
        
        if api_url:
            # Convert https://... -> wss://...
            # Convert http://... -> ws://...
            if api_url.startswith("https"):
                ws_base = api_url.replace("https", "wss")
            elif api_url.startswith("http"):
                ws_base = api_url.replace("http", "ws")
            else:
                ws_base = f"wss://{api_url}"
        else:
            # Local fallback
            ws_base = "ws://localhost:8000"
            
        context['ws_url'] = f"{ws_base}/api/support/ws/{ticket_id}?token={context['admin_ws_token']}"

        # Inject admin context for sidebar
        from django.contrib import admin
        context['app_label'] = 'web'
        context['model_name'] = 'support'
        context.update(admin.site.each_context(self.request))
        return context

def resolve_ticket(request, ticket_id):
    if not request.user.is_staff:
        return redirect('admin:login')
        
    if request.method == 'POST':
        success = TicketRepository.resolve(ticket_id)
        if success:
            messages.success(request, f'Ticket {ticket_id} resolved.')
        else:
            messages.error(request, 'Failed to resolve ticket.')
            
    return redirect('web:support_list')
