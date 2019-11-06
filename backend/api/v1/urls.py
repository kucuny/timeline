from django.urls import path, include


urlpatterns = [
    path('accounts/', include(('api.v1.accounts.urls', 'api_v1_accounts'), namespace='accounts')),
]
