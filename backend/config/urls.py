from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

urlpatterns = [
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('admin/', admin.site.urls),
    path('auth/api/', include('rest_framework.urls')),
    path('auth/social/', include('social_django.urls', namespace='social')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
