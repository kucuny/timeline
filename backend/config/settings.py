import os

import environ


# Read from .env
env = environ.Env()
env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'constance',
    'django_extensions',
    'rest_framework',
    'social_django',
]
INTERNAL_APPS = [
    'api',
    'contents',
    'users',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + INTERNAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': env.db('DJANGO_DEFAULT_DB')
}

# Caches
CACHES = {
    'default': env.cache('DJANGO_CACHE_DEFAULT'),
    'session': env.cache('DJANGO_CACHE_SESSION'),
    'auth': env.cache('DJANGO_CACHE_AUTH'),
}

# Django sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session'
SESSION_COOKIE_AGE = 60 * 60 * 24  # A day

# Authentication
AUTH_USER_MODEL = 'users.User'
AUTH_USERNAME_DELEGATOR_FIELD = 'email'
LOGIN_REDIRECT_URL = '/'

# Social auth configurations
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = []

SOCIAL_AUTH_ENABLED_FEATURES = env.list('SOCIAL_AUTH_ENABLED_FEATURES')
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'accounts.social_auth.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

if 'facebook' in SOCIAL_AUTH_ENABLED_FEATURES:
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS.append('social_core.backends.facebook.FacebookOAuth2')
    SOCIAL_AUTH_FACEBOOK_KEY = env.str('SOCIAL_AUTH_FACEBOOK_KEY')
    SOCIAL_AUTH_FACEBOOK_SECRET = env.str('SOCIAL_AUTH_FACEBOOK_SECRET')
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
    SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
        'locale': 'en_US',
        'fields': 'id, name, email',
    }

if 'google' in SOCIAL_AUTH_ENABLED_FEATURES:
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS.append('social_core.backends.google.GoogleOAuth2')
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env.str('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env.str('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
    SOCIAL_AUTH_GOOGLE_OAUTH2_USE_UNIQUE_USER_ID = True
    SOCIAL_AUTH_GOOGLE_OAUTH2_USERNAME_IS_FULL_EMAIL = True

if 'github' in SOCIAL_AUTH_ENABLED_FEATURES:
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS.append('social_core.backends.github.GithubOAuth2')
    SOCIAL_AUTH_GITHUB_KEY = env.str('SOCIAL_AUTH_GITHUB_KEY')
    SOCIAL_AUTH_GITHUB_SECRET = env.str('SOCIAL_AUTH_GITHUB_SECRET')

if 'kakao' in SOCIAL_AUTH_ENABLED_FEATURES:
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS.append('social_core.backends.kakao.KakaoOAuth2')
    SOCIAL_AUTH_KAKAO_KEY = env.str('SOCIAL_AUTH_KAKAO_KEY')
    SOCIAL_AUTH_KAKAO_SECRET = env.str('SOCIAL_AUTH_KAKAO_SECRET')

if 'naver' in SOCIAL_AUTH_ENABLED_FEATURES:
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS.append('social_core.backends.naver.NaverOAuth2')
    SOCIAL_AUTH_NAVER_KEY = env.str('SOCIAL_AUTH_NAVER_KEY')
    SOCIAL_AUTH_NAVER_SECRET = env.str('SOCIAL_AUTH_NAVER_SECRET')

if 'twitter' in SOCIAL_AUTH_ENABLED_FEATURES:
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS.append('social_core.backends.twitter.TwitterOAuth')
    SOCIAL_AUTH_TWITTER_KEY = env.str('SOCIAL_AUTH_TWITTER_KEY')
    SOCIAL_AUTH_TWITTER_SECRET = env.str('SOCIAL_AUTH_TWITTER_SECRET')

# Authentication Backend
DEFAULT_AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
AUTHENTICATION_BACKENDS = SOCIAL_AUTH_AUTHENTICATION_BACKENDS + DEFAULT_AUTHENTICATION_BACKENDS


# DRF Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentications.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

LOGGING_FORMATTERS = {
    'verbose': {
        'format': '{asctime} {levelname} {name}[{process}] {module}:{lineno} {message}',
        'style': '{',
        'datefmt': '%Y-%m-%d %H:%M:%S%z',
    },
    'query': {
        'format': '{asctime} {levelname} {name}[{process}] {module}:{lineno} {duration} {sql} args={params}',
        'style': '{',
        'datefmt': '%Y-%m-%d %H:%M:%S%z',
    },
    'migration': {
        'format': '{asctime} {levelname} {name}[{process}] {module}:{lineno} {sql} args={params}',
        'style': '{',
        'datefmt': '%Y-%m-%d %H:%M:%S%z',
    },
}
LOGGING_FILTERS = {
    'require_debug_true': {
        '()': 'django.utils.log.RequireDebugTrue'
    }
}
LOGGING_HANDLERS = {
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
    'debug': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'filters': ['require_debug_true'],
        'formatter': 'verbose',
    },
    'console_django_request': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
    'console_django_server': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
    'console_django_template': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
    'console_django_query': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'filters': ['require_debug_true'],
        'formatter': 'query',
    },
    'console_django_migration': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'filters': ['require_debug_true'],
        'formatter': 'migration',
    }
}
LOGGING_LOGGERS = {
    'django': {
        'handlers': ['console'],
    },
    # 'django.request': {
    #     'handlers': ['console_django_request'],
    # },
    # 'django.server': {
    #     'handlers': ['console_django_server'],
    # },
    # 'django.template': {
    #     'handlers': ['console_django_template'],
    # },
    # 'django.db.backends': {
    #     'handlers': ['console_django_query'],
    # },
    # 'django.db.backends.schema': {
    #     'handlers': ['console_django_migration'],
    # },
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': LOGGING_FORMATTERS,
    'filters': LOGGING_FILTERS,
    'handlers': LOGGING_HANDLERS,
    'loggers': LOGGING_LOGGERS,
}

# Django Constance
CONSTANCE_BACKEND = 'constance.backends.redisd.RedisBackend'
CONSTANCE_REDIS_CONNECTION = env('DJANGO_CONSTANCE_CACHE')
CONSTANCE_REDIS_PREFIX = 'constance:timeline:'
CONSTANCE_CONFIG = {
    'GOOGLE_OAOTH2_API_SECRET': (
        '',
        'Google oauth2 api secret',
    ),
    'GOOGLE_PHOTO_API_TOKEN': (
        '',
        'Google photo token',
    ),
}

# Google API
GOOGLE_OAUTH2_URL = 'https://accounts.google.com/o/oauth2/v2/auth'

# Google API Permission (Scopt)
GOOGLE_PHOTO_PERMISSION_SCOPES = (
    'https://www.googleapis.com/auth/photoslibrary.readonly',
)
