from datetime import date
from urllib.parse import urljoin

from django.core.exceptions import ValidationError

from libs.google.consts import GooglePhotosFeatureType, GooglePhotosMediaType
from libs.google.oauth2 import GoogleClient


MAX_PAGE_SIZE = 50
GOOGLE_PHOTOS_API_V1_BASE_URL = 'https://photoslibrary.googleapis.com/v1/'


# TODO: Refactoring
class GooglePhotoV1Client:
    def __init__(self, google_client: GoogleClient):
        self.google_client = google_client

    def albums(self):
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

            albums.extend(result['albums'])
            next_page_token = result.get('nextPageToken')

            if not next_page_token:
                break

        return albums

    def album(self, album_id):
        endpoint = urljoin(GOOGLE_PHOTOS_API_V1_BASE_URL, f'albums/{album_id}')
        response = self.google_client.session.get(endpoint)
        result = response.json()
        return result

    def media_items(self):
        endpoint = urljoin(GOOGLE_PHOTOS_API_V1_BASE_URL, 'mediaItems')

        params = {
            'pageSize': MAX_PAGE_SIZE,
        }
        media_items = []
        next_page_token = None
        while True:
            if next_page_token:
                params['pageToken'] = next_page_token

            response = self.google_client.session.get(endpoint, params=params)
            result = response.json()
            if not result:
                break

            media_items.extend(result['mediaItems'])
            next_page_token = result.get('nextPageToken')

            if not next_page_token:
                break

        return media_items

    def media_item(self, media_item_id: str):
        endpoint = urljoin(GOOGLE_PHOTOS_API_V1_BASE_URL, f'mediaItems/{media_item_id}')
        response = self.google_client.session.get(endpoint)
        result = response.json()
        return result

    def batch_get_media_items(self, media_item_ids: list):
        endpoint = urljoin(GOOGLE_PHOTOS_API_V1_BASE_URL, f'/v1/mediaItems:batchGet')

        params = {
            'mediaItemIds': media_item_ids,
        }
        response = self.google_client.session.get(endpoint, params=params)
        result = response.json()['mediaItemResults']
        return [item['mediaItem'] for item in result]

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

            media_items.extend(result['mediaItems'])
            next_page_token = result.get('nextPageToken')

            if not next_page_token:
                break

        return media_items

    def search_media_items_by_date(self, date_: date):
        filters = {
            'dateFilter':  {
                'dates': {
                    'year': date_.year,
                    'month': date_.month,
                    'day': date_.day,
                },
            },
        }
        return self._search_media_items(filters=filters)

    def search_media_items_by_date_range(self, start_date: date, end_date: date):
        filters = {
            'dateFilter': {
                'ranges': {
                    'startDate': {
                        'year': start_date.year,
                        'month': start_date.month,
                        'day': start_date.day,
                    },
                    'endDate': {
                        'year': end_date.year,
                        'month': end_date.month,
                        'day': end_date.day,
                    },
                },
            },
        }
        return self._search_media_items(filters=filters)

    def search_media_items_by_album_id(self, album_id: str):
        return self._search_media_items(album_id=album_id)

    def search_favorite_media_items(self):
        filters = {
            'featureFilter': {
                'includedFeatures': [
                    GooglePhotosFeatureType.FAVORITES.value,
                ],
            },
        }
        return self._search_media_items(filters=filters)

    def search_mediatype_media_items(self, media_type: GooglePhotosMediaType):
        filters = {
            'mediaTypeFilter': {
                'mediaTypes': [
                    media_type.value,
                ],
            },
        }
        return self._search_media_items(filters=filters)
