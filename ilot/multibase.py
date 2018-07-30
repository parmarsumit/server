import re
from ilot.core.models import request_switch, request_lock

from django.conf import settings
from django.db.models import ObjectDoesNotExist
from django.http import Http404
import os
import logging
logger = logging.getLogger(__name__)
from ilot.core.manager import AppManager
import traceback
import datetime
from django.db.models import Q, F
from ilot.core.models import Item
from ilot.models import Organization, Interface

# http://stackoverflow.com/questions/27401779/dynamically-set-database-based-on-request-in-django

def switch_request(host, url, akey, interface=None):

    #print('------- START SW')
    #    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    request_lock.acquire()

    request_switch.host = host
    request_switch.url = url

    request_host_parts = request_switch.host.split(':')

    if len(request_host_parts) == 2:
        request_switch.port = request_host_parts[1]
    else:
        request_switch.port = None

    request_switch.akey = akey

    from ilot.models import Interface

    if not interface:
        interface = Interface.objects.get(cname=host.split(':')[0])
    
    request_switch.interface = interface
    request_switch.organization = interface.application

    semester = datetime.timedelta(6*30)

    request_switch.end = AppManager.get_valid_time()
    request_switch.start = request_switch.end - semester

    host_name = host.split(':')[0]
    alias = None



def clear_switch():
    request_switch.organization = None
    request_switch.akey = None

    request_switch.port = None
    request_switch.host = ''
    request_switch.url = None

    request_lock.release()


class RouterMiddleware(object):

    def process_request(self, request):
        host = request.get_host().split(':')[0]
        url = request.build_absolute_uri()

        # first we check for an existing organisation
        try:
            interface = Interface.objects.get(cname=host)
            request_switch.interface = interface
            request_switch.organization = organization = interface.application
        except Interface.DoesNotExist:
            raise Http404

        # then, is the user authenticated ?
        from ilot.core.views.pipe import ActionPipeView
        akey = ActionPipeView.get_request_akey(request)

        switch_request(request.get_host(), url, akey)

        if request.path == '/deploy.json':
            setattr(request, '_dont_enforce_csrf_checks', True)

        return None

    def process_response( self, request, response ):
        try:
            clear_switch()
        except:
            pass
        return response

    def process_exception(self, request, exception):

        # send email to admin
        error_stack = traceback.format_exc()

        from ilot.views.front import get_context_dict
        from django.core.exceptions import PermissionDenied

        if exception.__class__ == PermissionDenied:
            return
        if exception.__class__ == Http404:
            return

        try:
            template_args = get_context_dict(request)
            organization = template_args['organization']

            if 'django/template' in error_stack:
                # we concider it's a template rendering error
                error_title = 'TMPL Error - '+organization.name+' ('+organization.cname+')'
            else:
                error_title = 'ILOT Error - '+organization.name+' ('+organization.cname+')'
        except:
            error_title = 'CORE Error - '+request.build_absolute_uri()

        request_data = ''
        request_data += request.build_absolute_uri()

        request_data += '\n\nREQUEST ----------------------\n\n'
        for key in sorted(request.META):
            if key.startswith('wsgi.'):
                continue
            request_data += key+': \n\t'+str(request.META[key])+'\n'

        request_data += '\n\n\nERROR ----------------------\n\n'
        request_data += error_stack

        if not settings.DEBUG:
            from django.core.mail import send_mail
            send_mail(error_title, request_data, settings.SERVER_EMAIL, settings.ADMINS, fail_silently=False)
