from django.contrib.auth import get_user_model
from django.core.cache import caches
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as DRFTokenAuthentication


User = get_user_model()


class TokenAuthentication(DRFTokenAuthentication):
    keyword = 'Token'
    cache = caches['auth']

    @classmethod
    def get_cache_key(cls, key):
        return f'token:{key}'

    def authenticate_credentials(self, key):
        token = self.cache.get(self.get_cache_key(key))
        if not token:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        user_id = token['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return user, token

    def authenticate_header(self, request):
        return self.keyword
