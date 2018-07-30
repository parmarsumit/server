'''
Created on 24 juin 2015

@author: rux
'''
import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.template.context import RequestContext, Context
from django.utils.text import slugify
from django.shortcuts import render_to_response
from django.template.base import Template
from ilot.core.models import Item, DataPath, Translation

from django.conf import settings
import mimetypes
from django.shortcuts import render
from ilot.core.models import request_switch, Moderation
from django.db.models import Q, F

from ilot.views.base import BaseView
from django.contrib import messages
from django.core.exceptions import PermissionDenied

try:
    from django.urls import resolve
except:
    from django.core.urlresolvers import resolve

from ilot.models import has_perm, filter_with_perm
import mimetypes
import logging
logger = logging.getLogger(__name__)

import operator
import re
import os

try:
    from urllib.parse import quote
except:
    from urllib import quote

try:
    from functools import reduce
except:
    pass


def get_input_data(request, **kwargs):
    """
    Get a dict of all the inputs merged ( GET < POST|json )

    The GET query keys are appended and updated
    by either the POST or the json['payload'] query keys

    You can change this behavior by overwritting this method in your view
    """
    data = {}
    # use the get variables first or last ?
    data.update(request.GET.dict())
    data.update(request.POST.dict())
    # remove csrftoken
    if 'csrfmiddlewaretoken' in data:
        del data['csrfmiddlewaretoken']

    return data

def get_user_profile(request, akey, input_data):
    return DataPath(akey=akey, context=akey)

def get_context_dict(request):
    """
    Return the main template args with page hierarchy
    """
    from django.core.exceptions import PermissionDenied

    akey = request.session.get('akey')
    input_data = get_input_data(request)
    user_profile = get_user_profile(request, akey, input_data)

    template_args = {'request':request}
    template_args['user_profile'] = user_profile
    template_args['input_data'] = input_data
    from django.contrib.messages import get_messages
    template_args['messages'] = get_messages(request)

    try:
        func, args, kwargs = resolve(request.path)
        template_args.update(kwargs)
        user_profile.action = kwargs['action']
    except:
        user_profile.action = 'index'

    #try:
    template_args['origin'] = user_profile
    #template_args['node'] = template_args['origin'].related

    return template_args


class FrontView(BaseView):
    """
    Display the service front page
    """
    view_name = "front"
    view_title = "Acceuil"
    default_action = 'index'


def handler500(request):
    template_args = get_context_dict(request)
    response = render_to_response(('500.html', 'ilot/500.html'), template_args)
    response.status_code = 500
    return response

def handler404(request):
    template_args = get_context_dict(request)
    response = render_to_response(('404.html', 'ilot/404.html'), template_args)
    response.status_code = 404
    return response

def handler403(request, close=False):
    """
    Unauthorized method
    """
    template_args = get_context_dict(request)
    response = render_to_response(('403.html', 'ilot/403.html'), template_args)
    response.status_code = 403
    return response

def handler402(request, close=False):
    """
    Payment required
    """
    template_args = get_context_dict(request)
    response = render_to_response(('402.html', 'ilot/402.html'), template_args)
    response.status_code = 402
    return response

def handler401(request, close=False):
    """
    Authentication Required
    """
    template_args = get_context_dict(request)
    response = render_to_response(('401.html', 'ilot/401.html'), template_args)
    response.status_code = 401
    return response
