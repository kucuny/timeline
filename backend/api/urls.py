from django.urls import path, include


urlpatterns = [
    path('v1/', include(('api.v1.urls', 'api_v1'), namespace='v1')),
]
