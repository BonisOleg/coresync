"""
Technicians URL Configuration.
"""
from django.urls import path
from . import views

app_name = 'technicians'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.TechnicianDashboardView.as_view(), name='dashboard'),
    
    # Work logs
    path('hours/log/', views.LogHoursAPIView.as_view(), name='log_hours'),
    path('hours/history/', views.WorkLogHistoryView.as_view(), name='work_history'),
    
    # Schedule management
    path('schedule/', views.AvailabilityCalendarView.as_view(), name='schedule'),
    path('schedule/<int:pk>/', views.ScheduleUpdateView.as_view(), name='schedule_update'),
    
    # Bookings assigned to technician
    path('bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
]

