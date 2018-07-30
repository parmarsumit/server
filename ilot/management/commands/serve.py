from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Deploy clusters  to scaleway infrastructure'

    def add_arguments(self, parser):
        from ilot.core.manager import AppManager
        parser.add_argument('--ip', type=str, default='127.0.0.1')
        parser.add_argument('--port', type=int, default=9999)

    def handle(self, *args, **options):
        from ilot.core.manager import AppManager
        from ilot.serve import serve
        from django.utils import translation
        translation.activate('en')
        serve(options['ip'], options['port'])
