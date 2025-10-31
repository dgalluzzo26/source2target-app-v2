"""
URL configuration for Source-to-Target Mapping Platform API.

This configuration provides:
- API documentation with Swagger/ReDoc
- User authentication and management endpoints
- Field mapping and data discovery endpoints
- Configuration management endpoints
- Admin interface for system management
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="API Root",
    description="Welcome to the Source-to-Target Mapping Platform API",
    responses={200: {"description": "API information"}}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint providing basic information about the platform.
    """
    return Response({
        "message": "Welcome to the Source-to-Target Mapping Platform API",
        "version": "2.0.0",
        "documentation": {
            "swagger": request.build_absolute_uri('/api/docs/swagger/'),
            "redoc": request.build_absolute_uri('/api/docs/redoc/'),
            "schema": request.build_absolute_uri('/api/docs/schema/')
        },
        "endpoints": {
            "accounts": request.build_absolute_uri('/api/accounts/'),
            "mapping": request.build_absolute_uri('/api/mapping/'),
            "config": request.build_absolute_uri('/api/config/'),
        }
    })


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api_root'),
    
    # API Documentation
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # App URLs
    path('api/accounts/', include('accounts.urls', namespace='accounts')),
    path('api/mapping/', include('mapping.urls', namespace='mapping')),
    path('api/config/', include('configuration.urls', namespace='config')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
