from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()

USER_FIELDS = ['username', 'email']


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    fields[User.USERNAME_FIELD] = fields[settings.AUTH_USERNAME_DELEGATOR_FIELD]

    if not fields:
        return

    return {
        'is_new': True,
        'user': strategy.create_user(**fields),
    }
