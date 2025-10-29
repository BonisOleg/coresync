"""
Technicians Views - Portal для technicians.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import Technician, WorkLog, Schedule
from .permissions import IsTechnicianOrManager


class TechnicianDashboardView(APIView):
    """
    Dashboard для technician - today's bookings, week hours total.
    """
    permission_classes = [IsAuthenticated, IsTechnicianOrManager]
    
    def get(self, request):
        try:
            technician = request.user.technician_profile
        except Technician.DoesNotExist:
            return Response({
                'error': 'Technician profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Today's bookings для technician
        today = timezone.now().date()
        from services.models import Booking
        
        today_bookings = Booking.objects.filter(
            technician=technician,
            booking_date=today,
            status__in=['confirmed', 'pending', 'in_progress']
        ).select_related('user', 'service').order_by('start_time')
        
        # Week hours total
        week_start = today - timedelta(days=today.weekday())
        weekly_hours = technician.get_weekly_hours_total(week_start)
        
        # Recent work logs
        recent_logs = WorkLog.objects.filter(
            technician=technician
        ).order_by('-date')[:7]
        
        return Response({
            'technician': {
                'name': technician.full_name,
                'email': technician.email,
                'specialties': technician.specialties,
                'hourly_rate': float(technician.hourly_rate)
            },
            'weekly_hours': float(weekly_hours),
            'today_bookings': [{
                'id': booking.id,
                'reference': booking.booking_reference,
                'service': booking.service.name,
                'client': booking.user.get_full_name(),
                'start_time': booking.start_time.isoformat(),
                'end_time': booking.end_time.isoformat(),
                'status': booking.status,
                'special_requests': booking.special_requests
            } for booking in today_bookings],
            'recent_logs': [{
                'id': log.id,
                'date': log.date.isoformat(),
                'hours': float(log.hours),
                'approved': log.approved,
                'notes': log.notes
            } for log in recent_logs]
        })


class LogHoursAPIView(APIView):
    """
    Log work hours - immediate sync до Google Sheets.
    """
    permission_classes = [IsAuthenticated, IsTechnicianOrManager]
    
    def post(self, request):
        try:
            technician = request.user.technician_profile
        except Technician.DoesNotExist:
            return Response({
                'error': 'Technician profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validate data
        date = request.data.get('date', timezone.now().date())
        hours = request.data.get('hours')
        notes = request.data.get('notes', '')
        
        if not hours:
            return Response({
                'error': 'Hours required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update work log
        work_log, created = WorkLog.objects.update_or_create(
            technician=technician,
            date=date,
            defaults={
                'hours': hours,
                'notes': notes
            }
        )
        
        # TODO: Trigger Google Sheets sync (після setup)
        # from .tasks import sync_worklog_to_sheets
        # sync_worklog_to_sheets.delay(work_log.id)
        
        return Response({
            'status': 'success',
            'work_log_id': work_log.id,
            'date': work_log.date.isoformat(),
            'hours': float(work_log.hours),
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class WorkLogHistoryView(APIView):
    """
    Work log history для technician.
    """
    permission_classes = [IsAuthenticated, IsTechnicianOrManager]
    
    def get(self, request):
        try:
            technician = request.user.technician_profile
        except Technician.DoesNotExist:
            return Response({
                'error': 'Technician profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get logs (last 30 days by default)
        days = int(request.query_params.get('days', 30))
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        logs = WorkLog.objects.filter(
            technician=technician,
            date__gte=cutoff_date
        ).order_by('-date')
        
        return Response({
            'logs': [{
                'id': log.id,
                'date': log.date.isoformat(),
                'hours': float(log.hours),
                'approved': log.approved,
                'synced': log.synced_to_sheets,
                'notes': log.notes
            } for log in logs],
            'total_hours': sum(float(log.hours) for log in logs if log.approved)
        })


class AvailabilityCalendarView(APIView):
    """
    Availability calendar - GET/PUT schedule.
    """
    permission_classes = [IsAuthenticated, IsTechnicianOrManager]
    
    def get(self, request):
        try:
            technician = request.user.technician_profile
        except Technician.DoesNotExist:
            return Response({
                'error': 'Technician profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        schedules = Schedule.objects.filter(
            technician=technician,
            is_active=True
        )
        
        return Response({
            'schedules': [{
                'id': schedule.id,
                'is_recurring': schedule.is_recurring,
                'weekday': schedule.weekday,
                'specific_date': schedule.specific_date.isoformat() if schedule.specific_date else None,
                'start_time': schedule.start_time.isoformat(),
                'end_time': schedule.end_time.isoformat(),
                'notes': schedule.notes
            } for schedule in schedules]
        })
    
    def post(self, request):
        """Create new schedule slot."""
        try:
            technician = request.user.technician_profile
        except Technician.DoesNotExist:
            return Response({
                'error': 'Technician profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # TODO: Implement schedule creation
        return Response({'status': 'TODO'}, status=status.HTTP_501_NOT_IMPLEMENTED)


class ScheduleUpdateView(APIView):
    """
    Update або delete schedule slot.
    """
    permission_classes = [IsAuthenticated, IsTechnicianOrManager]
    
    def put(self, request, pk):
        # TODO: Implement
        return Response({'status': 'TODO'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def delete(self, request, pk):
        # TODO: Implement
        return Response({'status': 'TODO'}, status=status.HTTP_501_NOT_IMPLEMENTED)


class MyBookingsView(APIView):
    """
    Bookings assigned to technician.
    """
    permission_classes = [IsAuthenticated, IsTechnicianOrManager]
    
    def get(self, request):
        try:
            technician = request.user.technician_profile
        except Technician.DoesNotExist:
            return Response({
                'error': 'Technician profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        from services.models import Booking
        
        # Фільтруємо по статусу та даті
        status_filter = request.query_params.get('status', 'all')
        days_ahead = int(request.query_params.get('days', 30))
        
        today = timezone.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        bookings = Booking.objects.filter(
            technician=technician,
            booking_date__gte=today,
            booking_date__lte=end_date
        ).select_related('user', 'service')
        
        if status_filter != 'all':
            bookings = bookings.filter(status=status_filter)
        
        bookings = bookings.order_by('booking_date', 'start_time')
        
        return Response({
            'bookings': [{
                'id': booking.id,
                'reference': booking.booking_reference,
                'service': booking.service.name,
                'client': booking.user.get_full_name(),
                'date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.isoformat(),
                'end_time': booking.end_time.isoformat(),
                'duration': booking.duration,
                'status': booking.status,
                'payment_status': booking.payment_status,
                'special_requests': booking.special_requests,
                'allergies_notes': booking.allergies_notes if hasattr(booking, 'allergies_notes') else ''
            } for booking in bookings],
            'total_count': bookings.count()
        })


class BookingDetailView(APIView):
    """
    Booking detail view для technician.
    Детальна інформація про конкретне бронювання.
    """
    permission_classes = [IsAuthenticated, IsTechnicianOrManager]
    
    def get(self, request, pk):
        try:
            technician = request.user.technician_profile
        except Technician.DoesNotExist:
            return Response({
                'error': 'Technician profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        from services.models import Booking
        
        try:
            booking = Booking.objects.select_related(
                'user', 'service', 'technician'
            ).get(id=pk)
            
            # Перевірка доступу - тільки assigned technician або manager
            if not request.user.is_staff and booking.technician != technician:
                return Response({
                    'error': 'Access denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            return Response({
                'id': booking.id,
                'reference': booking.booking_reference,
                'service': {
                    'id': booking.service.id,
                    'name': booking.service.name,
                    'duration': booking.duration,
                },
                'client': {
                    'name': booking.user.get_full_name(),
                    'email': booking.user.email,
                    'phone': booking.user.phone_number if hasattr(booking.user, 'phone_number') else ''
                },
                'schedule': {
                    'date': booking.booking_date.isoformat(),
                    'start_time': booking.start_time.isoformat(),
                    'end_time': booking.end_time.isoformat(),
                    'duration': booking.duration
                },
                'status': booking.status,
                'payment_status': booking.payment_status,
                'special_requests': booking.special_requests,
                'allergies_notes': booking.allergies_notes if hasattr(booking, 'allergies_notes') else '',
                'medical_notes': booking.medical_notes if hasattr(booking, 'medical_notes') else '',
                'scene_preferences': booking.scene_preferences if hasattr(booking, 'scene_preferences') else {},
                'technician_notes': booking.technician_notes,
                'created_at': booking.booked_at.isoformat() if hasattr(booking, 'booked_at') else None,
                'confirmed_at': booking.confirmed_at.isoformat() if booking.confirmed_at else None
            })
        
        except Booking.DoesNotExist:
            return Response({
                'error': 'Booking not found'
            }, status=status.HTTP_404_NOT_FOUND)
