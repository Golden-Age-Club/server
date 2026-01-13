from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('dashboard/', views.AdminDashboardView.as_view(), name='dashboard'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<str:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<str:pk>/toggle/', views.UserToggleStatusView.as_view(), name='user_toggle'),
    
    # Finance
    path('transactions/', views.TransactionListView.as_view(), name='transactions_list'),
    path('reports/', views.DailyReportView.as_view(), name='reports'),
]
