import json
import os
import webbrowser

from constance import config
from django.conf import settings
from requests_oauthlib import OAuth2Session


class GoogleClient:
    def __init__(self, secret_filepath=None, token=None):
        self.auth_url = settings.GOOGLE_OAUTH2_URL
        self.secret_filepath = secret_filepath
        self.session = None

        self._secret_data = None
        self._token = token

        self.authenticated = False

    @property
    def token(self):
        if self._token:
            return self._token

        try:
            token = json.loads(config.GOOGLE_PHOTO_API_TOKEN)
            self._token = token
        except (json.decoder.JSONDecodeError, TypeError):
            return None

        return self._token

    @property
    def secret_data(self):
        if self.secret_filepath and os.path.exists(self.secret_filepath):
            with open(self.secret_filepath, 'r') as f:
                self._secret_data = json.load(f)['installed']
        else:
            self._secret_data = json.loads(config.GOOGLE_OAOTH2_API_SECRET)['installed']

        return self._secret_data

    def update_token(self, token):
        self._token = token
        setattr(config, 'GOOGLE_PHOTO_API_TOKEN', json.dumps(token))

    def authorize(self):
        secret_data = self.secret_data
        client_id = secret_data['client_id']
        client_secret = secret_data['client_secret']
        redirect_uri = secret_data['redirect_uris'][0]
        token_uri = secret_data['token_uri']

        if self.token:
            oauth2_request_params = {
                'client_id': client_id,
                'token': self.token,
                'auto_refresh_url': token_uri,
                'auto_refresh_kwargs': {
                    'client_id': client_id,
                    'client_secret': client_secret
                },
                'token_updater': self.update_token,
            }
        else:
            oauth2_request_params = {
                'client_id': client_id,
                'scope': settings.GOOGLE_PHOTO_PERMISSION_SCOPES,
                'redirect_uri': redirect_uri,
            }

        self.session = OAuth2Session(**oauth2_request_params)

        if not self.token:
            user_authorization_url = self.session.authorization_url(self.auth_url)[0]
            print(user_authorization_url)
            webbrowser.open(user_authorization_url)
            auth_code = input('Input generated auth code : ')
            token = self.session.fetch_token(token_uri, client_secret=client_secret, code=auth_code)
            self.update_token(token)

        self.authenticated = True
