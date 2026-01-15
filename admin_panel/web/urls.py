from django.urls import path
from web.views import dashboard, users, finance, support

app_name = 'web'

urlpatterns = [
    # Dashboard
    path('dashboard/', dashboard.AdminDashboardView.as_view(), name='dashboard'),
    
    # Reports
    path('reports/', finance.DailyReportView.as_view(), name='reports'),
    # path('api/reports/daily/', dashboard.DailyStatsApiView.as_view(), name='api_daily_stats'),
    
    # User Management
    path('users/', users.UserListView.as_view(), name='user_list'),
    path('users/<str:pk>/', users.UserUpdateView.as_view(), name='user_detail'),
    path('users/<str:pk>/toggle/', users.UserToggleStatusView.as_view(), name='user_toggle'),
    # path('users/<str:user_id>/bonus/', management.AddBonusView.as_view(), name='add_bonus'), 
    
    # Transactions
    path('transactions/', finance.TransactionListView.as_view(), name='transactions_list'),
    
    # Integration
    # path('integration/telegram/', integration.TelegramConfigView.as_view(), name='telegram_config'),
    # path('integration/payment/', integration.PaymentConfigView.as_view(), name='payment_config'),

    # Support System (New)
    path('support/', support.TicketListView.as_view(), name='support_list'),
    path('support/<str:ticket_id>/', support.TicketChatView.as_view(), name='support_chat'),
    path('support/<str:ticket_id>/resolve/', support.resolve_ticket, name='resolve_ticket'),
]
