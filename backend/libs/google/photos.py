from urllib.parse import urljoin

from django.core.exceptions import ValidationError

from libs.google.oauth2 import GoogleClient


MAX_PAGE_SIZE = 50
GOOGLE_PHOTOS_API_V1_BASE_URL = 'https://photoslibrary.googleapis.com/v1/'


class GooglePhotoV1Client:
    def __init__(self, google_client: GoogleClient):
        self.google_client = google_client

    def album_list(self):
        endpoint = urljoin(GOOGLE_PHOTOS_API_V1_BASE_URL, 'albums')

        params = {
            'pageSize': MAX_PAGE_SIZE,
        }
        albums = []
        next_page_token = None
        while True:
            if next_page_token:
                params['pageToken'] = next_page_token

            response = self.google_client.session.get(endpoint, params=params)
            result = response.json()
            if not result:
                break

            albums.append(result['albums'])
            next_page_token = result.get('nextPageToken')

            if not next_page_token:
                break

        return albums

    def album(self, album_id):
        endpoint = urljoin(GOOGLE_PHOTOS_API_V1_BASE_URL, f'albums/{album_id}')
        response = self.google_client.session.get(endpoint)
        result = response.json()
        return result

    def _search_media_items(self, album_id: str = None, filters: dict = None):
        endpoint = urljoin(GOOGLE_PHOTOS_API_V1_BASE_URL, '/v1/mediaItems:search')
        params = {
            'pageSize': MAX_PAGE_SIZE,
        }

        if album_id and filters:
            raise ValidationError('album_id and filters cannot be set together.')

        if album_id:
            params['albumId'] = album_id
        elif filters:
            params['filters'] = filters

        media_items = []
        next_page_token = None
        while True:
            if next_page_token:
                params['pageToken'] = next_page_token

            response = self.google_client.session.post(endpoint, json=params)
            result = response.json()
            if not result:
                break

            media_items.append(result['mediaItems'])
            next_page_token = result.get('nextPageToken')

            if not next_page_token:
                break

        return media_items

    def search_media_items_by_album_id(self, album_id):
        return self._search_media_items(album_id=album_id)

    def search_favorite_media_items(self):
        filters = {
            'featureFilter': {
                'includedFeatures': [
                    'FAVORITES',
                ],
            },
        }
        return self._search_media_items(filters=filters)
