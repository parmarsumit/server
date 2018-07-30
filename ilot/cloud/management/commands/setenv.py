#
# seed
# -> create default items
# -> clean all models for nulls
# -> clean migrations
# export fixtures ??
#
# we got release 1 ?
from django.core.management.base import BaseCommand
from ilot.core.parsers.api_json import load_json, dump_json
import os
import uuid

try:
    from urllib.parse import quote
except:
    from urllib import quote

class Command(BaseCommand):
    help = 'Set a server setting key'

    def add_arguments(self, parser):
        parser.add_argument('key', nargs=1, type=str, default=False)
        parser.add_argument('value', nargs=1, type=str, default=False)

    def handle(self, *args, **options):
        from django.conf import settings
        from ilot.cloud.models import Container

        env_key = options['key'][0]
        env_value = options['value'][0]

        # get the container
        container = Container.objects.get(name='localhost')

        for service in container.services.all():
            settings = service.get_data()
            settings[env_key] = env_value
            service.settings = dump_json(settings)
            service.save()

        print(settings)
