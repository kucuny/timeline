from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('admin/', admin.site.urls),
    path('auth/api/', include('rest_framework.urls')),
    path('auth/social/', include('social_django.urls', namespace='social')),
]
