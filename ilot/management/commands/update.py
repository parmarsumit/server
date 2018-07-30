from django.core.management.base import BaseCommand
from django.template import loader, Context
from django.core.serializers import serialize
from django.core import serializers
import os

class Command(BaseCommand):
    help = 'Import last releases'

    def handle(self, *args, **options):
        from django.conf import settings
        from ilot.core.models import request_switch
        from django.core.management import call_command
        import hashlib
        import datetime

        from django.utils import translation
        translation.activate('en')

        #last_release = organization.get_last_release()

        model_results = {}
        from ilot.models import Interface, Organization, Release, Package
        from ilot.rules.models import Action, Attribute, Condition, Property, Requirement, Rule, Status, Trigger, Type
        from ilot.grammar.models import Message, Notification, Panel
        from ilot.webhooks.models import Webhook

        for Model in (Organization, Interface, Release, Package,
                      Action, Attribute, Condition, Property, Requirement, Rule, Status, Trigger, Type,
                      Message, Notification, Panel,
                      Webhook):

            nodes = Model.objects.all().order_by('ref_time')
            for node in nodes:
                model_results[node.id] = node

        #
        import ilot
        lib_path = os.path.dirname(os.path.dirname(ilot.__file__))

        # for each json file since last release
        model_ids = []
        for deserialized_object in serializers.deserialize("json", open(lib_path+'/application.json', 'r')):
            deserialized_object.save()
            model_ids.append( deserialized_object.object.id )

        return
        # remove objects not in release
        for model_id in model_results.keys():
            if not model_id in model_ids:
                node = model_results[model_id]
                print('Deleting ', node.__class__, node.id)
                node.delete()

        print('Updated ')
