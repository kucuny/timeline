from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.accounts import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
