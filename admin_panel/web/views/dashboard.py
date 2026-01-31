from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from repository.users import UserRepository
from repository.transactions import TransactionRepository
import json
from datetime import datetime

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super(AdminDashboardView, self).get_context_data(**kwargs)
        
        # 1. KPI Cards
        context['total_users'] = UserRepository.get_total_users()
        context['ggr'] = TransactionRepository.get_stats_ggr()
        
        monthly_stats = TransactionRepository.get_monthly_stats()
        context['total_deposits'] = monthly_stats.get('deposit', 0)
        context['total_withdrawals'] = monthly_stats.get('withdrawal', 0)
        
        # 2. Recent Transactions (Last 10)
        # Using existing repo method, simplified
        recent_tx_data = TransactionRepository.get_transactions(page=1, page_size=10)
        context['recent_transactions'] = recent_tx_data['items']
        
        # 3. Chart Data (Placeholder for now, or simple mock)
        # In a real app, this would be a separate API or complex aggregation
        context['chart_data'] = json.dumps({
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "datasets": [
                {
                    "label": "Deposits",
                    "data": [12, 19, 15, 25, 22, 33, 40],
                    "borderColor": "#28a745",
                    "backgroundColor": "rgba(40, 167, 69, 0.1)",
                    "fill": True,
                    "tension": 0.4
                },
                {
                    "label": "Withdrawals",
                    "data": [2, 3, 10, 5, 11, 14, 20],
                    "borderColor": "#dc3545",
                    "backgroundColor": "rgba(220, 53, 69, 0.1)",
                    "fill": True,
                    "tension": 0.4
                }
            ]
        })
        
        context['app_label'] = 'web'
        context['model_name'] = 'management'
        context.update(admin.site.each_context(self.request))
        return context
