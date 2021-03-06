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
MAX_ITEMS = 50


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
            '--sync-favorite-photos',
            dest='sync_favorite_photos',
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
        albums = list(GooglePhotoAlbum.objects.all().values('id', 'album_id', 'title', 'total_count', 'is_public'))
        pprint(albums)

    def sync_albums(self):
        albums = self.gp_client.albums()
        for album in tqdm(albums):
            params = {
                'title': album['title'],
                'total_count': album.get('mediaItemsCount', 0),
                'product_url': album['productUrl'],
                'cover_photo_url': album['coverPhotoBaseUrl'],
            }
            GooglePhotoAlbum.objects.update_or_create(album_id=album['id'],
                                                      defaults=params)

    def sync_photos(self, target_album_id=None, target_date=None, target_start_date=None, target_end_date=None):
        if target_album_id:
            album = GooglePhotoAlbum.objects.get(album_id=target_album_id)
            print(f'Album title : {album.title}')
            photos = self.gp_client.search_media_items_by_album_id(target_album_id)
        elif target_date:
            photos = self.gp_client.search_media_items_by_date(target_date)
        else:
            photos = self.gp_client.search_media_items_by_date_range(target_start_date, target_end_date)

        imported_at = timezone.now()
        synced_photo = []
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
            item, _ = GooglePhotoItem.objects.update_or_create(item_id=photo['id'], defaults=params)
            synced_photo.append(item)

        if target_album_id:
            album.photo_items.add(*synced_photo)

    def migrate_items(self, path, album_id=None, item_ids=None):
        path = path if path else DEFAULT_SAVED_PHOTOS_PATH
        filters = {
            'is_public': True,
            'migrated_at__isnull': True,
        }
        if album_id:
            filters['albums__album_id'] = album_id
        else:
            item_ids = item_ids.split(',')
            filters['item_id__in'] = item_ids

        photos = GooglePhotoItem.objects.filter(**filters).order_by('shooting_at')
        if not photos.exists():
            return

        update_migrated_at_item_ids = []
        except_item_ids = []
        paging = Paginator(photos, MAX_ITEMS)
        for page in tqdm(paging.page_range, desc='Pages'):
            photo_ids = list(paging.page(page).object_list.values_list('item_id', flat=True))
            photos_from_gphotos = self.gp_client.batch_get_media_items(photo_ids)

            for photo in tqdm(photos_from_gphotos, desc=f'{page} Page of {paging.num_pages}'):
                photo_meta = photo['mediaMetadata']
                url = (
                    photo['baseUrl'] + '=dv-d'
                    if photo['mimeType'].startswith('video')
                    else photo['baseUrl'] + f'=w{photo_meta["width"]}-h{photo_meta["height"]}-d'
                )
                response = requests.get(url, stream=True)
                if response.ok:
                    shooting_at = parse(photo_meta['creationTime'])
                    filename = f'{shooting_at.strftime("%Y%m%d")}_{shooting_at.strftime("%H%M%S")}_{photo["filename"]}'
                    try:
                        with open(f'{path}/{filename}', 'wb') as f:
                            f.write(response.content)
                        update_migrated_at_item_ids.append(photo['id'])
                    except IOError as e:
                        except_item_ids.append(photo['id'])
                        continue
        GooglePhotoItem.objects.filter(item_id__in=update_migrated_at_item_ids).update(migrated_at=timezone.now())
        print(except_item_ids)

    def handle(self, *args, **options):
        show_albums = options['show_albums']
        sync_albums = options['sync_albums']

        sync_photos = options['sync_photos']
        target_album_id = options['target_album_id']
        target_date = options['target_date']
        target_start_date = options['target_start_date']
        target_end_date = options['target_end_date']

        sync_favorite_photos = options['sync_favorite_photos']

        migrate_photos = options['migrate_photos']
        target_path = options['target_path']
        target_item_ids = options['target_item_ids']

        if show_albums:
            self.show_albums()
            return

        if sync_albums or sync_photos or sync_favorite_photos or migrate_photos:
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
        elif sync_favorite_photos:
            photos = self.gp_client.search_favorite_media_items()
            ids = {photo['id'] for photo in photos}
            GooglePhotoItem.objects.filter(item_id__in=ids).update(favorite=True)
        elif migrate_photos:
            if not target_item_ids and not target_album_id:
                raise CommandError('You must set --target-item-ids or --target-album-id')

            if target_item_ids:
                self.migrate_items(path=target_path, item_ids=target_item_ids)
            if target_album_id:
                self.migrate_items(path=target_path, album_id=target_album_id)
