import json
import os
import webbrowser

from constance import config
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from requests_oauthlib import OAuth2Session


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--secret-file',
            dest='secret_file',
            type=str,
            default=None,
        )

    def save_token(self, token):
        setattr(config, 'GOOGLE_PHOTO_API_TOKEN', token)

    def handle(self, *args, **options):
        secret_file = options['secret_file']
        if not secret_file or not os.path.exists(secret_file):
            raise CommandError('Secret file does not exist.')

        with open(secret_file, 'r') as f:
            secret_data = json.load(f)['installed']

        client_id = secret_data['client_id']
        client_secret = secret_data['client_secret']
        redirect_uri = secret_data['redirect_uris'][0]
        token_uri = secret_data['token_uri']

        saved_token = config.GOOGLE_PHOTO_API_TOKEN
        if saved_token:
            oauth2_request_params = {
                'client_id': client_id,
                'token': saved_token,
                'auto_refresh_url': token_uri,
                'auto_refresh_kwargs': {
                    'client_id': client_id,
                    'client_secret': client_secret
                },
                'token_updater': self.save_token,
            }
        else:
            oauth2_request_params = {
                'client_id': client_id,
                'scope': settings.GOOGLE_PHOTO_PERMISSION_SCOPES,
                'redirect_uri': redirect_uri,
            }
        session = OAuth2Session(**oauth2_request_params)

        if not saved_token:
            user_authorization_url = session.authorization_url(settings.GOOGLE_OAUTH2_URL)
            webbrowser.open(user_authorization_url[0])
            auth_code = input('Input generated auth code : ')
            token = session.fetch_token(token_uri, client_secret=client_secret, code=auth_code)
            self.save_token(token)
