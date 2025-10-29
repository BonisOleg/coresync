"""
Analytics URL Configuration.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Reports
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
    path('reports/membership/', views.membership_report, name='membership_report'),
    
    # API endpoints
    path('api/data/', views.AnalyticsAPIView.as_view(), name='api_data'),
    
    # Export
    path('export/', views.export_data_view, name='export_data'),
]
