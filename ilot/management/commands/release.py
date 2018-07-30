from django.core.management.base import BaseCommand
from django.template import loader, Context
from django.core.serializers import serialize

import os

class Command(BaseCommand):
    help = 'Release last changes'

    def add_arguments(self, parser):
        return
        parser.add_argument('cname',
                            dest='cname',
                            type=str
                            )

        parser.add_argument('name',
                            dest='name',
                            type=str
                            )

    def handle(self, *args, **options):

        # ensure we are not on production
        from django.conf import settings

        if not settings.DEBUG or os.environ.get('DJANGO_ENV') == 'production':
            print('You are not allowed to release from production environement')
            return

        from ilot.core.models import request_switch
        from django.core.management import call_command
        import hashlib
        import datetime

        from django.utils import translation
        translation.activate('en')

        #call_command('clean_ab', project=CloudManager.get_project_id(), verbosity=1, interactive=False)
        from django.core.management import call_command
        #call_command('migrate', database=CloudManager.get_project_id(), verbosity=1, interactive=False, load_initial_data=False)

        model_results = []

        from ilot.models import Interface, Organization, Release, Package
        from ilot.rules.models import Action, Attribute, Condition, Property, Requirement, Rule, Status, Trigger, Type
        from ilot.grammar.models import Message, Notification, Panel
        from ilot.webhooks.models import Webhook

        for Model in (Status, Type, Action, Attribute, Condition, Property, Requirement, Rule, Trigger,
                      Interface, Organization, Release, Package, Message, Webhook, Notification, Panel):

            nodes = Model.objects.all().order_by('ref_time')

            for node in nodes:
                model_results.append(node)

        model_data = serialize("json", model_results)

        import ilot
        lib_path = os.path.dirname(os.path.dirname(ilot.__file__))
        subfolder = lib_path+''
        os.system('mkdir -p '+subfolder)

        f = open(subfolder+'/application.json', "w")
        f.write(model_data)
        f.close()

        print('SERIALIZED ', len(model_results), 'to ', subfolder+'/application.json')
        return

        print('EXPORTED TO '+subfolder)


        model_results = []

        from ilot.webhooks.models import Webhook
        from ilot.rules.models import Action, Attribute, Condition, Property, Requirement, Rule, Status, Trigger, Type
        from ilot.grammar.models import Message, Notification, Panel
        from ilot.models import Interface, Organization, Release, Package

        for Model in (Webhook, Status, Type, Action, Attribute, Condition, Property, Requirement, Rule, Trigger,
                      Message, Notification, Panel,
                      Interface, Organization, Release, Package):
            if since:
                nodes = Model.objects.filter( Q(modified_date__gt=since)|Q(created_date__gt=since)).order_by('modified_date', 'created_date')
            else:
                nodes = Model.objects.all().order_by('ref_time')

            for node in nodes:
                model_results.append(node)

        print('TOTAL', len(model_results))
