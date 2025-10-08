"""
URL configuration for CoreSync project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import JsonResponse

def api_health(request):
    return JsonResponse({
        'status': 'success',
        'message': 'CoreSync API is running',
        'version': '1.0.0',
        'debug': True
    })

def api_test(request):
    return JsonResponse({
        'message': 'API endpoints working',
        'available_endpoints': [
            '/api/health/',
            '/api/services/', 
            '/api/memberships/plans/',
            '/api/users/profile/'
        ]
    })

urlpatterns = [
    # Frontend pages (NEW DESIGN!)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('private/', TemplateView.as_view(template_name='private.html'), name='private'),
    path('menssuite/', TemplateView.as_view(template_name='menssuite.html'), name='menssuite'),
    path('membership/', TemplateView.as_view(template_name='membership.html'), name='membership'),
    path('contacts/', TemplateView.as_view(template_name='contacts.html'), name='contacts'),
    path('book/', TemplateView.as_view(template_name='booking_calendar.html'), name='booking_calendar'),
    
    # Services pages
    path('services/', TemplateView.as_view(template_name='services/list.html'), name='services_list'),
    path('services/<slug:slug>/', TemplateView.as_view(template_name='services/detail.html'), name='service_detail'),
    
    # Shop pages (NEW)
    path('shop/', TemplateView.as_view(template_name='shop/index.html'), name='shop_index'),
    path('shop/cart/', TemplateView.as_view(template_name='shop/cart.html'), name='shop_cart'),
    
    # Concierge pages (NEW)
    path('concierge/', TemplateView.as_view(template_name='concierge/request.html'), name='concierge_request'),
    
    # Content pages
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('technologies/', TemplateView.as_view(template_name='pages/technologies.html'), name='technologies'),
    
    # Legal pages (NEW)
    path('privacy-policy/', TemplateView.as_view(template_name='legal/privacy_policy.html'), name='privacy_policy'),
    path('terms/', TemplateView.as_view(template_name='legal/terms.html'), name='terms'),
    path('refund-policy/', TemplateView.as_view(template_name='legal/refund_policy.html'), name='refund_policy'),
    
    # Authentication pages
    path('login/', TemplateView.as_view(template_name='auth/login.html'), name='login'),
    path('signup/', TemplateView.as_view(template_name='auth/signup.html'), name='signup'),
    path('password-reset/', TemplateView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    
    # Dashboard pages (open for demo, add login_required later)
    path('dashboard/', TemplateView.as_view(template_name='dashboard/overview.html'), name='dashboard_overview'),
    path('dashboard/bookings/', TemplateView.as_view(template_name='dashboard/bookings.html'), name='dashboard_bookings'),
    path('dashboard/membership/', TemplateView.as_view(template_name='dashboard/membership.html'), name='dashboard_membership'),
    path('dashboard/profile/', TemplateView.as_view(template_name='dashboard/profile.html'), name='dashboard_profile'),
    path('logout/', TemplateView.as_view(template_name='dashboard/logout.html'), name='logout'),
    
    # Admin panel (PRESERVED!)
    path('admin/', admin.site.urls),
    
    # API health check (PRESERVED!)
    path('api/health/', api_health, name='api_health'),
    path('health/', api_health, name='health_check'),  # For Render health check
    path('api/test/', api_test, name='api_test'),
    
    # SEO
    path('sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml',
        content_type='application/xml'
    ), name='sitemap'),
    
    # NEW API ROUTES (FIXED INTEGRATION)
    path('', include('services.urls')),      # Services API
    path('', include('memberships.urls')),   # Memberships API  
    path('', include('users.urls')),         # Users API
    path('', include('services.booking_urls')),  # Booking Calendar API - ENABLED!
    path('', include('shop.urls')),          # Shop API - NEW!
    path('', include('concierge.urls')),     # Concierge API - NEW!
    # path('', include('payments.urls')),      # Payments & QuickBooks API - DISABLED FOR INITIAL DEPLOY
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
