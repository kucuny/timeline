from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.accounts import views


app_name = 'accounts'


router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
