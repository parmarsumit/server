from tornado import websocket
from ilot.manager import OnlineManager
from ilot.core.manager import AppManager
import json

try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

from django.conf import settings
import traceback
from ilot.core.views.pipe import ActionPipeView

from ilot.views.front import FrontView

from django.db.models import ObjectDoesNotExist
from ilot.models import Organization

from ilot.multibase import switch_request, clear_switch
from django.http.response import Http404
from django.core.exceptions import PermissionDenied

from ilot.core.parsers.api_json import load_json, dump_json

from django.contrib.sessions.models import Session
#from user_sessions.models import Session


import time

def user_from_session_key(session_key):
    from django.conf import settings
    from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
    from django.contrib.auth.models import AnonymousUser

    session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    session_wrapper = session_engine.SessionStore(session_key)
    user_id = session_wrapper.get(SESSION_KEY)

    if session_wrapper.get(BACKEND_SESSION_KEY):
        auth_backend = load_backend(session_wrapper.get(BACKEND_SESSION_KEY))

        if user_id and auth_backend:
          return auth_backend.get_user(user_id)
        else:
          return AnonymousUser()
    else:
        return AnonymousUser()


from ilot.core.models import Moderation
from django.db.models.signals import post_save
from django.dispatch import receiver
from ilot.manager import OnlineManager

online_manager = OnlineManager.get_instance()
from ilot.core.models import request_switch

from ilot.models import Interface

#
# @receiver(post_save, sender=Moderation)
# def broadcast_m_event(sender, instance, **kwargs):
#
#     data = {
#         'akey':instance.akey,
#         'action':instance.action,
#         'status':instance.status,
#         'uri':instance.related.id,
#         'value':instance.value,
#         'data':instance.data,
#         'from':instance.get_profile().get_full_name(),
#     }
#     if not hasattr(request_switch, 'equeue'):
#         request_switch.equeue = []
#
#     for member in instance.related.get_memberships():
#         print('SENDING '+instance.action+' TO '+member.akey)
#         request_switch.equeue.append((member.akey, data))


online_manager = OnlineManager.get_instance()


class ActionSocket(websocket.WebSocketHandler):
    _ready = True
    organization = None

    def open(self):

        #
        online_manager.wsockets.append(self)

        #
        if not 'sessionid' in self.request.cookies:
            self.close()
            return

        # path is the room where the user is arriving
        # we create a room per registred user ?
        session_id = self.request.cookies['sessionid'].value

        # get django session data
        try:
            session = Session.objects.get(session_key=session_id)
            session_data = session.get_decoded()
        except Session.DoesNotExist:
            session_data = {}
            session_data['akey'] = AppManager.get_new_uuid()
            #return

        #
        akey = session_data['akey']
        self.request.akey = akey
        self.request.path = akey

        from ilot.core.models import Item
        try:
            actor = Item.objects.get(id=akey)
        except ObjectDoesNotExist:
            actor = Item(id=akey,
                         locale=akey,
                          context=akey,
                          origin_id=akey,
                          target=akey,
                          related_id=akey,
                          akey=akey,
                          status='newVisitor')
            actor.save()

        # generate wkey ?
        wkey = online_manager.get_contact_uuid()
        online_manager.akey_by_wkey[wkey] = akey
        online_manager.register_online(self, wkey)
        #online_manager.join_network()

        # send it to the connecting user
        kwargs = {
            'context':session_data['akey'],
            'path':session_data['akey'],
            'input_data':{},
            'action':'index',
            'ext':'.html',
            'do':True,
            'todo':True,
            'text':'Welcome to the network. Please Authenticate or register',
        }
        #self.on_message(json.dumps(kwargs))
        #self.send_content(wkey.encode('UTF8'), kwargs)


    def check_origin(self, origin):

        if not origin in online_manager.domain_websockets:
            online_manager.domain_websockets[origin] = []

        online_manager.domain_websockets[origin].append(self)
        online_manager.websocket_domain[self] = origin
        parsed_origin = urlparse(origin)

        try:
            host_name = parsed_origin.netloc.split(':')[0]
            if host_name in AppManager.organization_by_host:
                self.organization = AppManager.organization_by_host[host_name]
            else:
                try:
                    self.organization = Organization.objects.get(cname=host_name)
                except:
                    self.organization = None
            return True
        except ObjectDoesNotExist:
            self.organization = Organization.objects.get(cname=None)
            return False



    def check_signature(self, signature):
        akey = None
        return akey

    def on_message(self, payload):

        enveloppe = json.loads(payload)
        print('NEW PAYLOAD', enveloppe)

        # verify the signature
        akey = self.check_signature(enveloppe)

        message = json.loads(enveloppe['message'])

        print('INCOMMING', message)

        session_data = {}
        session_data['akey'] = self.request.akey

        self.request.input_data = {}
        self.request.GET = {}
        self.request.POST = {}
        self.request.FILES = {}
        self.request.META = {}
        #self.request.user = user_from_session_key(session_id)
        self.request.session = session_data

        kwargs = {
            'context':session_data['akey'],
            'path':session_data['akey'],
            'input_data':{},
            'action':'index',
            'ext':'.html',
            'do':False,
        }

        self.request.kwargs = kwargs

        url = 'ws'+self.request.full_url()[4:]

        if message['interface']:
            interface = Interface.objects.get(id=message['interface'])
            switch_request(self.request.host, url, session_data['akey'], interface=interface)
        else:
            switch_request(self.request.host, url, session_data['akey'])

        try:
            enveloppe = message
            input_data = enveloppe.get('input_data')
            kwargs.update(enveloppe)

            self.request.kwargs = kwargs
            if kwargs['do']:
                self.request.method = 'POST'
                self.request.POST = input_data
            else:
                self.request.method = 'GET'
                self.request.GET = input_data

            #
            self.request.path = kwargs['path']
            print('WS :', request_switch.interface.cname, kwargs)

            self.request.host = request_switch.host = request_switch.interface.cname

            response = self.pre_process(self.request, ws=self, **kwargs)

            #print(response.content)

            data = self.send_content(response.content, kwargs)
            # manage events triggers
            #if hasattr(request_switch, 'equeue'):
            #    for e in request_switch.equeue:
            #        online_manager.broadcast_event(e[0], e[1])
            #    request_switch.equeue = []

        except Http404:
            traceback.print_exc()
            print('WS 404')
            self.send_content(b'404', kwargs)

        except PermissionDenied:
            print('WS 403')
            # render permission denied page ?
            self.send_content(b'403', kwargs)

        except:
            traceback.print_exc()
            message = {'error':'content from request ?'}
            self.send_content(json.dumps(message), kwargs)
        finally:
            clear_switch()


        # check for profile permissions
        if True == False:
            # register the item-action for this ws if not already done ...
            item_action = kwargs['path']+'-'+kwargs['action']
            if not item_action in online_manager.ws_by_item_action:
                online_manager.ws_by_item_action[item_action] = []
            if not self in online_manager.ws_by_item_action[item_action]:
                online_manager.ws_by_item_action[item_action].append(self)

            if not self in online_manager.item_action_by_ws:
                online_manager.item_action_by_ws[self] = []
            if not item_action in online_manager.item_action_by_ws[self]:
                online_manager.item_action_by_ws[self].append(item_action)
            #
            # data = {
            #     'akey':instance.akey,
            #     'action':instance.action,
            #     'status':instance.status,
            #     'uri':instance.related.id,
            #     'value':instance.value,
            #     'data':instance.data,
            #     'from':instance.get_profile().get_full_name(),
            # }
            # if not hasattr(request_switch, 'equeue'):
            #     request_switch.equeue = []
            #
            # for member in instance.related.get_memberships():
            #     print('SENDING '+instance.action+' TO '+member.akey)
            #     request_switch.equeue.append((member.akey, data))
            #
            #if True == False:
                #data = self.send_content(response.content, kwargs)


    def render(self, request, template_args, **kwargs):
        return ActionPipeView.render(self, request, template_args, **kwargs)

    def send_content(self, content, kwargs):
        kwargs['data'] = content.decode('utf-8')
        message = dump_json(kwargs)
        self.send_safe(message)
        return kwargs

    def send_safe(self, message):
        try:
            while not self._ready:
                time.sleep(0.05)
            self._ready = False
            self.write_message(message)
            self._ready = True
        except:
            traceback.print_exc()
        finally:
            self._ready = True

    def Zsend_content(self, content, kwargs):
        kwargs['data'] = content.decode('utf-8')
        try:
            while not self._ready:
                time.sleep(0.05)
            self._ready = False
            self.write_message(dump_json(kwargs))
            self._ready = True
        except:
            traceback.print_exc()
        finally:
            self._ready = True
        return kwargs

    def on_close(self):
        online_manager = OnlineManager.get_instance()
        online_manager.unregister_online(self)
        online_manager.wsockets.remove(self)

        # when the websocket connection is lost
        # the aky is removed from the connected users
        # we apply a delay of 5 or 10 seconds to remove it from the list
        # and concider the user offline because he can be simply browsing the website


class OnlineSocket(ActionSocket, FrontView):
    pass
