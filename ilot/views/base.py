'''
Created on 24 juin 2015

@author: rux
'''
import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.text import slugify
from django.http.response import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template.base import Template
from django.template.context import RequestContext
from ilot.core.models import Item, DataPath

from django.core.paginator import Paginator
from django.http.response import HttpResponse

from ilot.core.manager import AppManager
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, AnonymousUser
from django.views.decorators.http import require_http_methods
from django.conf import settings
import mimetypes
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from ilot.core.models import request_switch, Moderation
from ilot.models import has_perm, filter_with_perm
from django.db.models import Q, F

from ilot.core.views.pipe import ActionPipeView
from ilot.multibase import switch_request

from ilot.core.parsers.api_json import load_json

import logging
logger = logging.getLogger(__name__)

from django.contrib import messages


from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


import operator
import re
import os

try:
    from functools import reduce
except:
    pass


class BaseView(ActionPipeView):
    """
    Display the service front page
    """
    view_name = "backend"
    view_title = "Backend"

    def get_context_dict(self, request, user_profile, input_data, **kwargs):

        organization = request_switch.organization

        template_args = super(BaseView, self).get_context_dict(request, user_profile, input_data, **kwargs)

        template_args['start'] = request_switch.start
        template_args['end'] = request_switch.end

        template_args['application'] = request_switch.organization
        template_args['interface'] = request_switch.interface

        template_args['currentNode'] = kwargs['node']
        template_args['origin'] = kwargs['origin']

        request_switch.context = kwargs['origin'].context

        from ilot.rules.models import Action
        template_args['action_item'] = Action.objects.get(name=kwargs['action'])
        template_args['action_panel'] = template_args['action_item'].get_panel()

        if input_data.get('query'):
            template_args['results'] = kwargs['origin'].do_query(input_data.get('query'))

        if settings.CLOUD:

            online_manager = OnlineManager.get_instance()
            online_keys = []
            for key in online_manager.network_visitors:
                online_keys.append(key)
            for key in online_manager.websockets_by_visitor:
                if not key in online_keys:
                    online_keys.append(key)

            online_visitors = []
            for key in online_keys:
                online_visitors.append(Item.objects.get_at_id(key))

            template_args['online_visitors'] = online_visitors

        return template_args

    def pre_process(self, request, input_data, **kwargs):

        akey = self.get_session_user_keys(request)
        action = kwargs['action']

        #switch_request(request_switch.host, request_switch.url, akey)

        #print('PROCESSING', kwargs['path'], kwargs['action'], kwargs['ext'], akey)
        # check if currentSession user exists
        try:
            actor = Item.objects.get(id=akey)
        except ObjectDoesNotExist:
            return self.authenticate_redirect(request, input_data, **kwargs)

        try:
            kwargs['origin'] = Moderation.objects.get(id=kwargs['path'])
            kwargs['node'] = kwargs['origin'].related
        except ObjectDoesNotExist:
            print('No item at', kwargs['path'])
            if not 'token' in kwargs:
                return self.authenticate_redirect(request, input_data, **kwargs)
            else:
                raise Http404

        kwargs['context'] = kwargs['origin'].get_context()

        print('SETTING', request_switch.host, request_switch.interface.cname)

        # manage token access
        if request.META.get('HTTP_X_TOKEN'):
            from ilot.models import Authorization
            # check for the profile with the corresponding token
            try:
                token = Authorization.objects.get(token=request.META.get('HTTP_X_TOKEN'),
                                                  action=kwargs['action'],
                                                  item=kwargs['node'].id,
                                                  enabled=True)
            except ObjectDoesNotExist:
                # there are no token corresponding so we reject the call
                messages.error(request, "Bad token")
                raise PermissionDenied

            request.session['akey'] = token.akey
            akey = request.session['akey']

        if settings.CLOUD:
            # check for ws keys request
            online_manager = OnlineManager.get_instance()

            wkey = online_manager.get_contact_uuid()

            online_manager.akey_by_wkey[wkey] = akey
            online_manager.wkey_by_akey[akey] = wkey

            if not akey in OnlineManager.profile_akeys:
                OnlineManager.profile_akeys[akey] = profile

        #kwargs['profile'] = profile

        try:
            # check for permissions
            if not has_perm(kwargs['action'], request_switch.organization, akey, item=kwargs['origin'], ext=kwargs['ext'], method=request.method):
                logger.error('Missing permission for '+akey+' '+str(kwargs))
                raise PermissionDenied
            else:
                check_requirements = False
                if check_requirements:
                    # check for requirements
                    from ilot.rules.models import Requirement
                    requirements = Requirement.objects.select_related().filter(action__name=kwargs['action'])
                    for requirement in requirements:
                        # check if requirement condition
                        condition_mod = kwargs['origin']
                        if requirement.reference == 'actor':
                            condition_mod = Item.objects.get_at_id(akey)
                        elif requirement.reference == 'item':
                            condition_mod = kwargs['node']

                        if not requirement.condition.is_true(condition_mod):
                            print('MISSING REQUIREMENT :', requirement.condition)
                            messages.warning(request, requirement.message)


                            kwargs['template'] = '403.html'
                            user_profile = self.get_user_profile(request, **kwargs)
                            template_args = self.get_context_dict(request, user_profile, input_data, **kwargs)

                            template_args['requirement'] = requirement

                            response = self.render(request, template_args, **kwargs)

                            return response

                if 'Zws' in kwargs:
                    ws = kwargs['ws']
                    from ilot.manager import OnlineManager
                    online_manager = OnlineManager.get_instance()

                    # register the item-action for this ws if not already done ...
                    item_action = kwargs['path']+'-'+kwargs['action']
                    if not item_action in online_manager.ws_by_item_action:
                        online_manager.ws_by_item_action[item_action] = []
                    if not ws in online_manager.ws_by_item_action[item_action]:
                        online_manager.ws_by_item_action[item_action].append(ws)

                    if not ws in online_manager.item_action_by_ws:
                        online_manager.item_action_by_ws[ws] = []
                    if not item_action in online_manager.item_action_by_ws[ws]:
                        online_manager.item_action_by_ws[ws].append(item_action)

            response = super(BaseView, self).pre_process(request, input_data, **kwargs)

        except PermissionDenied:
            #if kwargs['node'].can_index:
            #    return HttpResponseRedirect(kwargs['node'].get_url())
            kwargs['template'] = '403.html'
            user_profile = self.get_user_profile(request, **kwargs)
            template_args = self.get_context_dict(request, user_profile, input_data, **kwargs)
            response = self.render(request, template_args, **kwargs)


        return response


    def authenticate_redirect(self, request, input_data, path, **kwargs):

        from ilot.models import Authorization
        # check for the profile with the corresponding token
        try:
            token = Authorization.objects.get(id=path)
            # have the authorization been used ?
            if token.enabled == False:

                if token.akey == request.session['akey']:
                    # redirect to origin
                    try:
                        mod = Moderation.objects.get(id=token.origin)
                    except ObjectDoesNotExist:
                        raise Http404
                    return HttpResponseRedirect(mod.get_url())
                else:
                    raise Http404

        except Authorization.DoesNotExist:

            akey = self.get_session_user_keys(request)

            if path == akey:
                print('HELLo')
                try:
                    actor = Item.objects.get(id=akey)
                except ObjectDoesNotExist:
                    actor = Item(id=akey,
                                  locale=request_switch.interface.id,
                                  context=akey,
                                  origin_id=akey,
                                  target=akey,
                                  related_id=akey,
                                  akey=akey,
                                  status='newVisitor')
                    actor.save()

                kwargs['node'] = actor
                kwargs['origin'] = kwargs['node'].origin

                kwargs['context'] = kwargs['origin'].get_context()
                kwargs['path'] = akey
                return self.pre_process(request, input_data, **kwargs)

            else:
                raise Http404

        # appli the authorization action with payload
        request.session['akey'] = token.akey
        request_switch.akey = token.akey

        #if request.session['akey'] != token.akey:
        print('GOT YOU IN !', token.akey, request.session['akey'])

        # here this should raise event

        #return HttpResponseRedirect(kwargs['path'])

        token.enabled = False
        token.save()

        input_data = load_json(token.payload)

        switch_request(request_switch.host, request_switch.url, token.akey)

        kwargs['do'] = True
        kwargs['action'] = token.action

        kwargs['token'] = token

        kwargs['path'] = token.origin # Moderation.objects.get(id=token.origin).get_url()+token.action+'/'
        kwargs['origin'] = Moderation.objects.get(id=token.origin)
        kwargs['node'] = kwargs['origin'].related

        kwargs['context'] = kwargs['origin'].get_context()

        response = super(BaseView, self).pre_process(request, input_data, **kwargs)
        #response = self.pre_process(request, input_data, **kwargs)
        return response

        #return Moderation.objects.get(id=token.origin).get_url()+token.action+'/'


    def close(self):
        print('CLOSE SENDING EVENTS')
        if hasattr(request_switch, 'Zequeue'):
            online_manager = OnlineManager.get_instance()
            for e in request_switch.equeue:
                online_manager.broadcast_event(e[0], e[1])
            request_switch.equeue = []
