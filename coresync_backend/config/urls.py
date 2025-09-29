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
    
    # Admin panel (PRESERVED!)
    path('admin/', admin.site.urls),
    
    # API health check (PRESERVED!)
    path('api/health/', api_health, name='api_health'),
    path('api/test/', api_test, name='api_test'),
    
    # NEW API ROUTES (FIXED INTEGRATION)
    path('', include('services.urls')),      # Services API
    path('', include('memberships.urls')),   # Memberships API  
    path('', include('users.urls')),         # Users API
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
