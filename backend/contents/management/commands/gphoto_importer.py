from datetime import datetime

from django.core.management import BaseCommand, CommandError
from django.utils import timezone
from tqdm import tqdm

from contents.models import GooglePhotoAlbum, GooglePhotoItem
from libs.google.consts import GooglePhotosMediaType
from libs.google.oauth2 import GoogleClient
from libs.google.photos import GooglePhotoV1Client


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--album',
            dest='target_album',
            action='store_true',
        )
        parser.add_argument(
            '--photo',
            dest='target_photo',
            action='store_true',
        )
        parser.add_argument(
            '--date',
            dest='target_date',
            type=str,
            default=None,
        )
        parser.add_argument(
            '--start_date',
            dest='target_start_date',
            type=str,
            default=None,
        )
        parser.add_argument(
            '--end_date',
            dest='target_end_date',
            type=str,
            default=None,
        )

    def initialize(self):
        google_client = GoogleClient()
        google_client.authorize()

        self.gp_client = GooglePhotoV1Client(google_client)

    def handle(self, *args, **options):
        target_album = options['target_album']
        target_photo = options['target_photo']
        target_date = options['target_date']

        if not target_album and not target_photo:
            raise CommandError('Add target (--album, --photo)')

        if target_photo:
            if not target_date:
                raise CommandError('You must set target date(--date) when import photos.')

            try:
                target_date = datetime.strptime(target_date, '%Y-%m-%d')
            except ValueError:
                raise CommandError('You must set valid target date(--date %Y-%m-%d).')


        self.initialize()

        if target_album:
            albums = self.gp_client.albums()
            for album in tqdm(albums):
                params = {
                    'title': album['title'],
                    'product_url': album['productUrl'],
                    'cover_photo_url': album['coverPhotoBaseUrl'],
                }
                GooglePhotoAlbum.objects.update_or_create(id=album['id'],
                                                          defaults=params)

        if target_photo:
            imported_at = timezone.now()
            photos = self.gp_client.search_media_items_by_date(target_date)
            for photo in tqdm(photos):
                photo_meta = photo['mediaMetadata']
                params = {
                    'product_url': photo['productUrl'],
                    'base_url': photo['baseUrl'],
                    'mine_type': photo['mimeType'],
                    'media_type': (GooglePhotosMediaType.VIDEO.value
                                   if photo['mimeType'].startswith('video')
                                   else GooglePhotosMediaType.PHOTO.value),
                    'weight': photo_meta['width'],
                    'height': photo_meta['height'],
                    'meta': photo_meta,
                    'imported_at': imported_at,
                }
                GooglePhotoItem.objects.update_or_create(id=photo['id'],
                                                         defaults=params)
