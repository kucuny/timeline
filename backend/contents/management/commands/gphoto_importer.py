import shutil
from datetime import datetime
from pprint import pprint

import requests
from django.core.management import BaseCommand, CommandError
from django.core.paginator import Paginator
from django.utils import timezone
from dateutil.parser import parse
from tqdm import tqdm

from contents.models import GooglePhotoAlbum, GooglePhotoItem
from libs.google.consts import GooglePhotosMediaType
from libs.google.oauth2 import GoogleClient
from libs.google.photos import GooglePhotoV1Client


DEFAULT_SAVED_PHOTOS_PATH = '/tmp/migrated'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--show-albums',
            dest='show_albums',
            action='store_true',
        )
        parser.add_argument(
            '--sync-albums',
            dest='sync_albums',
            action='store_true',
        )
        parser.add_argument(
            '--sync-photos',
            dest='sync_photos',
            action='store_true',
        )
        parser.add_argument(
            '--migrate-photos',
            dest='migrate_photos',
            action='store_true',
        )
        parser.add_argument(
            '--target-album-id',
            dest='target_album_id',
            type=str,
            default=None,
        )
        parser.add_argument(
            '--target-item-ids',
            dest='target_item_ids',
            type=str,
            default=None,
        )
        parser.add_argument(
            '--target-path',
            dest='target_path',
            type=str,
            default=None,
        )
        parser.add_argument(
            '--target-date',
            dest='target_date',
            type=str,
            default=None,
        )
        parser.add_argument(
            '--target-start-date',
            dest='target_start_date',
            type=str,
            default=None,
        )
        parser.add_argument(
            '--target-end-date',
            dest='target_end_date',
            type=str,
            default=None,
        )

    def initialize(self):
        google_client = GoogleClient()
        google_client.authorize()

        self.gp_client = GooglePhotoV1Client(google_client)

    def show_albums(self):
        albums = list(GooglePhotoAlbum.objects.all().values('id', 'title', 'is_public'))
        pprint(albums)

    def sync_albums(self):
        albums = self.gp_client.albums()
        for album in tqdm(albums):
            params = {
                'title': album['title'],
                'product_url': album['productUrl'],
                'cover_photo_url': album['coverPhotoBaseUrl'],
            }
            GooglePhotoAlbum.objects.update_or_create(id=album['id'],
                                                      defaults=params)

    def sync_photos(self, target_album_id=None, target_date=None, target_start_date=None, target_end_date=None):
        if target_album_id:
            album = GooglePhotoAlbum.objects.get(pk=target_album_id)
            print(album.title)
            photos = self.gp_client.search_media_items_by_album_id(target_album_id)
        elif target_date:
            photos = self.gp_client.search_media_items_by_date(target_date)
        else:
            photos = self.gp_client.search_media_items_by_date_range(target_start_date, target_end_date)

        imported_at = timezone.now()
        for photo in tqdm(photos):
            photo_meta = photo['mediaMetadata']
            shooing_at = parse(photo_meta['creationTime'])
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
                'shooting_at': shooing_at,
                'shooting_date': shooing_at,
            }
            if target_album_id:
                params['album_id'] = target_album_id
            GooglePhotoItem.objects.update_or_create(id=photo['id'],
                                                     defaults=params)

    def migrate_photos_from_item_ids(self, path, target_item_ids=None):
        path = path if path else DEFAULT_SAVED_PHOTOS_PATH
        item_ids = target_item_ids.split(',')
        imported_photos = GooglePhotoItem.objects.filter(id__in=item_ids, is_public=True).only('product_url')
        photos = self.gp_client.batch_get_media_items(list(imported_photos.values_list('id', flat=True)))

        for photo in photos:
            photo_meta = photo['mediaMetadata']
            url = photo['baseUrl'] + f'=w{photo_meta["width"]}-h{photo_meta["height"]}'
            response = requests.get(url, stream=True)
            if response.ok:
                shooting_at = parse(photo_meta['creationTime'])
                filename = f'{shooting_at.strftime("%Y%m%d")}_{shooting_at.strftime("%H%M%S")}_{photo["filename"]}'
                try:
                    with open(f'{path}/{filename}', 'wb') as f:
                        f.write(response.content)
                    GooglePhotoItem.objects.filter(pk=photo['id']).update(migrated_at=timezone.now())
                except IOError:
                    pass

    def migrate_photos_from_album_id(self, path, target_album_id=None):
        path = path if path else DEFAULT_SAVED_PHOTOS_PATH
        photos = GooglePhotoItem.objects.filter(album_id=target_album_id, is_public=True).values_list('pk', flat=True)
        paging = Paginator(photos, 50)
        for page in range(paging.num_pages):
            import pdb; pdb.set_trace()
            photo_ids = list(paging.page(page + 1))
            photos_from_gphotos = self.gp_client.batch_get_media_items(photo_ids)

            for photo in photos_from_gphotos:
                photo_meta = photo['mediaMetadata']
                url = photo['baseUrl'] + f'=w{photo_meta["width"]}-h{photo_meta["height"]}'
                response = requests.get(url, stream=True)
                if response.ok:
                    shooting_at = parse(photo_meta['creationTime'])
                    filename = f'{shooting_at.strftime("%Y%m%d")}_{shooting_at.strftime("%H%M%S")}_{photo["filename"]}'
                    try:
                        with open(f'{path}/{filename}', 'wb') as f:
                            f.write(response.content)
                        GooglePhotoItem.objects.filter(pk=photo['id']).update(migrated_at=timezone.now())
                    except IOError:
                        pass

    def handle(self, *args, **options):
        show_albums = options['show_albums']
        sync_albums = options['sync_albums']

        sync_photos = options['sync_photos']
        target_album_id = options['target_album_id']
        target_date = options['target_date']
        target_start_date = options['target_start_date']
        target_end_date = options['target_end_date']

        migrate_photos = options['migrate_photos']
        target_path = options['target_path']
        target_item_ids = options['target_item_ids']

        if show_albums:
            self.show_albums()
            return

        if sync_albums or sync_photos or migrate_photos:
            self.initialize()
        else:
            raise CommandError('You must set --sync-albums or --sync-photos.')

        if sync_albums:
            self.sync_albums()
        elif sync_photos:
            if target_album_id:
                self.sync_photos(target_album_id=target_album_id)
            elif target_date:
                try:
                    target_date = datetime.strptime(target_date, '%Y-%m-%d')
                except ValueError:
                    raise CommandError('You must set valid target target_date(--target_date %Y-%m-%d).')
                self.sync_photos(target_date=target_date)
            elif target_start_date and target_end_date:
                try:
                    target_start_date = datetime.strptime(target_start_date, '%Y-%m-%d')
                    target_end_date = datetime.strptime(target_end_date, '%Y-%m-%d')
                except ValueError:
                    raise CommandError('You must set valid target target_date(--target_date %Y-%m-%d).')
                self.sync_photos(target_start_date=target_start_date, target_end_date=target_end_date)
        elif migrate_photos:
            if not target_item_ids and not target_album_id:
                raise CommandError('You must set --target-item-ids or --target-album-id')

            # TODO: mov 인 경우 chuck 처리
            if target_item_ids:
                self.migrate_photos_from_item_ids(path=target_path, target_item_ids=target_item_ids)
            if target_album_id:
                self.migrate_photos_from_album_id(path=target_path, target_album_id=target_album_id)
