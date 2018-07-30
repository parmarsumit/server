from django.http.response import Http404, HttpResponse
from ilot.views.front import FrontView
from django.conf import settings
from ilot.core.models import request_switch
from ilot.core.manager import AppManager

import os

import mimetypes


class SiteView(FrontView):
    """
    Serve site files
    """
    def get(self, request, *args, **kwargs):
        """
        Manage a GET request
        """
        akey = self.get_session_user_keys(request)
        if kwargs['path']:
            kwargs['template'] = 'app/'+kwargs['path']+kwargs['ext']
        kwargs['action'] = request.GET.get('action', request_switch.interface.action.name)
        kwargs['path'] = request.GET.get('id', akey)
        kwargs['context'] = akey
        return super(FrontView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Manage a POST request
        """
        akey = self.get_session_user_keys(request)
        if kwargs['path']:
            kwargs['template'] = 'app/'+kwargs['path']+kwargs['ext']
        kwargs['action'] = request.GET.get('action', request_switch.interface.action.name)
        kwargs['path'] = request.GET.get('id', akey)
        kwargs['context'] = akey
        return super(FrontView, self).post(request, *args, **kwargs)
