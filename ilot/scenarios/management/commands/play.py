from django.core.management.base import BaseCommand
from django.template import loader, Context
from django.core.serializers import serialize
from django.core import serializers
import os

import logging

logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("py.warnings").setLevel(logging.ERROR)

class Command(BaseCommand):
    help = 'Play the scenario'

    def add_arguments(self, parser):
        parser.add_argument('name', nargs=1, type=str, default=False)

    def handle(self, *args, **options):

        from ilot.core.models import request_switch
        from django.core.management import call_command
        import hashlib
        import datetime

        from django.utils import translation
        translation.activate('en')

        scenario_name = options['name'][0]

        from ilot.scenarios.models import Scenario
        scenario = Scenario.objects.get(name=scenario_name)
        scenario.run()
