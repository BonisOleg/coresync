"""
Analytics Views - Admin dashboard and reporting.
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser


@staff_member_required
def dashboard_view(request):
    """
    Main analytics dashboard для admin.
    Shows key metrics, charts, reports.
    """
    from services.models import Booking
    from memberships.models import Membership
    from notifications.models import EmailLog
    from ai_agent.models import Conversation
    
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Key metrics
    context = {
        # Bookings
        'total_bookings': Booking.objects.count(),
        'bookings_this_month': Booking.objects.filter(
            booking_date__gte=month_ago
        ).count(),
        'bookings_today': Booking.objects.filter(
            booking_date=today
        ).count(),
        
        # Revenue (approximate)
        'revenue_this_month': Booking.objects.filter(
            booking_date__gte=month_ago,
            payment_status='paid'
        ).aggregate(
            total=Sum('final_total')
        )['total'] or 0,
        
        # Memberships
        'active_members': Membership.objects.filter(
            status='active'
        ).count(),
        'new_members_this_month': Membership.objects.filter(
            created_at__gte=month_ago
        ).count(),
        
        # AI Agent
        'ai_conversations': Conversation.objects.count(),
        'ai_bookings': Conversation.objects.filter(
            booking__isnull=False
        ).count(),
        
        # Emails
        'emails_sent': EmailLog.objects.filter(
            status='sent'
        ).count(),
        'emails_this_week': EmailLog.objects.filter(
            created_at__gte=week_ago
        ).count(),
    }
    
    return render(request, 'analytics/dashboard.html', context)


@staff_member_required
def revenue_report(request):
    """Revenue breakdown report."""
    from services.models import Booking
    
    # Get date range від query params
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    bookings = Booking.objects.filter(
        booking_date__gte=start_date,
        payment_status='paid'
    )
    
    # Group by day
    daily_revenue = bookings.values('booking_date').annotate(
        count=Count('id'),
        total=Sum('final_total')
    ).order_by('booking_date')
    
    context = {
        'daily_revenue': list(daily_revenue),
        'total_revenue': bookings.aggregate(Sum('final_total'))['final_total__sum'] or 0,
        'total_bookings': bookings.count(),
        'average_booking': bookings.aggregate(Avg('final_total'))['final_total__avg'] or 0,
        'days': days
    }
    
    return render(request, 'analytics/revenue_report.html', context)


@staff_member_required
def membership_report(request):
    """Membership analytics."""
    from memberships.models import Membership
    
    memberships = Membership.objects.filter(status='active')
    
    # Group by tier
    by_tier = memberships.values('tier').annotate(
        count=Count('id')
    )
    
    context = {
        'total_members': memberships.count(),
        'by_tier': list(by_tier),
        'churn_rate': 0,  # TODO: Calculate
        'lifetime_value': 0,  # TODO: Calculate
    }
    
    return render(request, 'analytics/membership_report.html', context)


class AnalyticsAPIView(APIView):
    """
    Analytics API для charts та dashboards.
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get analytics data в JSON format."""
        from services.models import Booking
        from memberships.models import Membership
        
        metric_type = request.query_params.get('type', 'overview')
        
        if metric_type == 'overview':
            return self._get_overview()
        elif metric_type == 'revenue':
            return self._get_revenue_data()
        elif metric_type == 'bookings':
            return self._get_bookings_data()
        elif metric_type == 'members':
            return self._get_members_data()
        
        return Response({'error': 'Invalid metric type'}, status=400)
    
    def _get_overview(self):
        """Overview metrics."""
        from services.models import Booking
        from memberships.models import Membership
        from ai_agent.models import Conversation
        
        today = timezone.now().date()
        month_ago = today - timedelta(days=30)
        
        data = {
            'bookings': {
                'total': Booking.objects.count(),
                'this_month': Booking.objects.filter(booking_date__gte=month_ago).count(),
                'confirmed': Booking.objects.filter(status='confirmed').count(),
            },
            'members': {
                'total': Membership.objects.filter(status='active').count(),
                'base': Membership.objects.filter(status='active', tier='base').count(),
                'premium': Membership.objects.filter(status='active', tier='premium').count(),
                'unlimited': Membership.objects.filter(status='active', tier='unlimited').count(),
            },
            'ai': {
                'conversations': Conversation.objects.count(),
                'conversion_rate': self._calculate_ai_conversion_rate(),
            }
        }
        
        return Response(data)
    
    def _get_revenue_data(self):
        """Revenue data для charts."""
        from services.models import Booking
        
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        daily_revenue = Booking.objects.filter(
            booking_date__gte=start_date,
            payment_status='paid'
        ).values('booking_date').annotate(
            revenue=Sum('final_total'),
            count=Count('id')
        ).order_by('booking_date')
        
        return Response({
            'daily_revenue': list(daily_revenue),
            'total': Booking.objects.filter(
                booking_date__gte=start_date,
                payment_status='paid'
            ).aggregate(Sum('final_total'))['final_total__sum'] or 0
        })
    
    def _get_bookings_data(self):
        """Bookings data."""
        from services.models import Booking
        
        bookings_by_service = Booking.objects.values(
            'service__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        bookings_by_status = Booking.objects.values(
            'status'
        ).annotate(
            count=Count('id')
        )
        
        return Response({
            'by_service': list(bookings_by_service),
            'by_status': list(bookings_by_status)
        })
    
    def _get_members_data(self):
        """Membership data."""
        from memberships.models import Membership
        
        growth = []
        for i in range(6, -1, -1):
            date = timezone.now().date() - timedelta(days=i*30)
            count = Membership.objects.filter(
                created_at__lte=date,
                status='active'
            ).count()
            growth.append({
                'date': date.isoformat(),
                'count': count
            })
        
        return Response({
            'growth': growth,
            'by_tier': list(Membership.objects.filter(
                status='active'
            ).values('tier').annotate(count=Count('id')))
        })
    
    def _calculate_ai_conversion_rate(self):
        """Calculate AI conversation → booking conversion."""
        from ai_agent.models import Conversation
        
        total = Conversation.objects.count()
        converted = Conversation.objects.filter(
            booking__isnull=False
        ).count()
        
        if total == 0:
            return 0
        
        return round((converted / total) * 100, 2)


@staff_member_required
def export_data_view(request):
    """Export data до Google Sheets або CSV."""
    export_type = request.GET.get('type', 'bookings')
    format_type = request.GET.get('format', 'csv')
    
    if export_type == 'bookings':
        return _export_bookings(format_type)
    elif export_type == 'members':
        return _export_members(format_type)
    elif export_type == 'revenue':
        return _export_revenue(format_type)
    
    return JsonResponse({'error': 'Invalid export type'}, status=400)


def _export_bookings(format_type):
    """Export bookings data."""
    from services.models import Booking
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Reference', 'Date', 'Time', 'Service', 'Client',
        'Status', 'Payment Status', 'Total'
    ])
    
    bookings = Booking.objects.all().select_related(
        'user', 'service'
    ).order_by('-booking_date')[:1000]
    
    for booking in bookings:
        writer.writerow([
            booking.booking_reference,
            booking.booking_date,
            booking.start_time,
            booking.service.name,
            booking.user.get_full_name(),
            booking.status,
            booking.payment_status,
            booking.final_total
        ])
    
    return response


def _export_members(format_type):
    """Export members data."""
    # TODO: Implement
    return JsonResponse({'status': 'TODO'})


def _export_revenue(format_type):
    """Export revenue data."""
    # TODO: Implement
    return JsonResponse({'status': 'TODO'})

