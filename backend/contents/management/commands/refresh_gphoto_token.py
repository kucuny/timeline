import json

from django.core.management import BaseCommand, CommandError

from libs.google.oauth2 import GoogleClient


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--secret-file',
            dest='secret_file',
            type=str,
            default=None,
        )

    def handle(self, *args, **options):
        secret_file = options['secret_file']
        google_client = GoogleClient(secret_file)
        google_client.authorize()
