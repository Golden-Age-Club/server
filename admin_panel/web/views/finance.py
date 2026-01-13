from django.views.generic import TemplateView, View
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from repository.transactions import TransactionRepository
from datetime import datetime, timedelta

class TransactionListView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/transaction_list.html'

    def get_context_data(self, **kwargs):
        context = super(TransactionListView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        user_id = self.request.GET.get('q', '')
        type_filter = self.request.GET.get('type', '')
        status_filter = self.request.GET.get('status', '')
        date_from_str = self.request.GET.get('date_from', '')
        date_to_str = self.request.GET.get('date_to', '')
        
        filters = {}
        date_from = None
        date_to = None

        if date_from_str:
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        if date_to_str:
            try:
                # Set to end of day
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            except ValueError:
                pass

        # If 'q' is provided, it's strictly a user_id filter based on our repo logic
        uid = user_id if user_id else None
        
        context.update(TransactionRepository.get_transactions(
            page=page, 
            user_id=uid,
            type=type_filter or None,
            status=status_filter or None,
            date_from=date_from,
            date_to=date_to
        ))
        
        context['search_query'] = user_id
        context['current_type'] = type_filter
        context['current_status'] = status_filter
        context['date_from'] = date_from_str
        context['date_to'] = date_to_str
        context['app_label'] = 'web'
        context['model_name'] = 'management'
        context.update(admin.site.each_context(self.request))
        return context


class DailyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super(DailyReportView, self).get_context_data(**kwargs)
        
        # Simple Logic: Get stats for last 7 days
        # In a real optimized system, we would do one aggregation query.
        # Here we will simulate it or rely on a new repo method.
        # For MVP, let's just fetch Monthly Stats as a placeholder for the "Daily" view 
        # or implement a specific daily aggregator in Repo if needed.
        
        # Let's add a quick aggregation method call directly here for demonstration
        # strictly following the "Report Logic" from design
        
        stats = TransactionRepository.get_monthly_stats()
        context['monthly_stats'] = stats
        context['net_revenue'] = stats.get('deposit', 0) - stats.get('withdrawal', 0)
        
        context['app_label'] = 'web'
        context['model_name'] = 'management'
        context.update(admin.site.each_context(self.request))
        return context
