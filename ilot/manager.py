from threading import Thread
from django.db.models import ObjectDoesNotExist
from django.db.models import Q

from django.conf import settings
from ilot.core.models import request_switch, request_lock

from datetime import datetime
import sys
import threading
import uuid
import os
import time

from pytz import timezone
import pytz
utc = pytz.utc
import json

from ilot.core.models import DataPath

from ilot.meta.models import MessageQueue


from ilot.core.parsers.api_json import dump_json


class OnlineManager(Thread):
    """
    Singleton that manages users online/offline and websockets messaging
    """
    _instance = None

    wsockets = []

    domain_websockets = {}
    websocket_domain = {}

    profile_akeys = {}

    akey_by_wkey = {}
    wkey_by_akey = {}
    wkey_by_websocket = {}
    websocket_by_wkey = {}

    visitors = []

    visitors_by_websocket = {}
    websockets_by_visitor = {}

    # [uri-action] = [ws, ws, ws]
    ws_by_item_action = {}
    item_action_by_ws = {}

    network_visitors = {}

    event_queue = []

    @classmethod
    def get_instance(cls):
        #if cls._instance:
        #    return cls._instance
        #with cls._instance_lock:
        if cls._instance is None:
            cls._instance = OnlineManager()
            cls._instance.start()
        return cls._instance

    @staticmethod
    def get_contact_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def get_ref_time():
        return int(time.time()*100000)

    @staticmethod
    def get_time():
        return datetime.utcnow()

    def get_process_id(self):
        return self.process_id

    def __init__(self, *args, **kwargs):
        """
        Not much to init ...
        """
        self.process_id = str(uuid.uuid4())
        self.process_time = OnlineManager.get_ref_time()

        self.do_polling = True

        super(OnlineManager, self).__init__(*args, **kwargs)

    def run(self):

        """ here comes the database polling """
        from ilot.core.models import Moderation
        from ilot.meta.models import MessageQueue
        while self.do_polling:
            request_lock.acquire()
            # get latest events
            last_mods = Moderation.objects.filter(ref_time__gt=self.process_time).order_by('ref_time')

            for mod in last_mods:
                # check for messages
                relay_messages = MessageQueue.objects.filter(process_id=self.process_id, event_id=mod.id)
                for message in relay_messages:
                    self.relay(message.actor_id, message.message)
                self.process_time = mod.ref_time

            #self.process_time = OnlineManager.get_ref_time()
            request_lock.release()

            time.sleep(1)

    def stop(self):

        self.do_polling = False

        # remove message queue process rows
        MessageQueue.objects.filter(process_id=self.process_id).delete()

        self.join()


    def notify(self, akey, data):
        event_data = dump_json(data)
        if akey in self.websockets_by_visitor:
            for ws in self.websockets_by_visitor[akey]:
                ws.send_safe(event_data)

    def relay(self, akey, string):
        if akey in self.websockets_by_visitor:
            for ws in self.websockets_by_visitor[akey]:
                ws.send_safe(string)

    def register_online(self, websocket, wkey, token=None):

        akey = self.akey_by_wkey[wkey]

        self.wkey_by_websocket[websocket] = wkey
        self.websocket_by_wkey[wkey] = websocket

        if not wkey in self.akey_by_wkey:
            # TODO
            # inform admin it's a security issue !
            print('WARNING : ', 'someone trying to provide unregistred wkey ', wkey)
            return

        # maybe akey has already wkey ?
        akey = self.akey_by_wkey[wkey]
        if akey in self.wkey_by_akey:
            # there is already a window with akey
            # that could be changed only by websocket accept/...
            #print('Window accept ?')
            #return
            pass

        #
        self.visitors_by_websocket[websocket] = akey

        if not akey in self.websockets_by_visitor:
            self.websockets_by_visitor[str(akey)] = []

        if not websocket in self.websockets_by_visitor[str(akey)]:
            self.websockets_by_visitor[str(akey)].append(websocket)


        markup = MessageQueue(process_id=self.process_id, actor_id=akey)
        markup.save()

        self.visitors.append({'socket':websocket, 'akey':akey, 'domain':self.websocket_domain[websocket]})

        #if settings.DEBUG:
        #    print('REGISTRED:', akey, wkey, CloudManager.get_process_id())

        #self.process_publisher.send_connected(akey, CloudManager.get_process_id())



    def unregister_online(self, websocket):

        if not websocket in self.visitors_by_websocket:
            # TODO
            # check why the websocket is not registred
            return

        wkey = self.wkey_by_websocket[websocket]

        # unset online the visitor
        akey = self.visitors_by_websocket[websocket]

        #if settings.DEBUG:
        #    print('UN-REGISTER:', akey, wkey, CloudManager.get_process_id())

            #dt = DataPath.objects.get(akey=akey, value=wkey, visible=True)
            #dt.visible=False
            #dt.save()

        if wkey in self.akey_by_wkey:
            del self.akey_by_wkey[wkey]
            # unregister only if websocket is

        if akey in self.wkey_by_akey:
            if self.wkey_by_akey[akey] == wkey:
                del self.wkey_by_akey[akey]
            else:
                # check if not idle ??
                pass

        self.websockets_by_visitor[akey].remove(websocket)
        if not len(self.websockets_by_visitor[akey]):
            del self.websockets_by_visitor[akey]

            # delete only if no more connection opened for the user
            mq = MessageQueue.objects.filter(process_id=self.process_id, actor_id=akey)
            mq.delete()
            #self.process_publisher.send_disconnected(akey, CloudManager.get_process_id())

        for visitor in self.visitors:
            if 'socket' in visitor and visitor['socket'] == websocket:
                self.visitors.remove(visitor)
                break



        del self.visitors_by_websocket[websocket]

        del self.websocket_by_wkey[wkey]
        del self.wkey_by_websocket[websocket]

        if websocket in self.item_action_by_ws:
            for item_action in self.item_action_by_ws[websocket]:
                self.ws_by_item_action[item_action].remove(websocket)
            if not len(self.ws_by_item_action[item_action]):
                del self.ws_by_item_action[item_action]

            del self.item_action_by_ws[websocket]

    # TODO
    # periodic tasks
    # - purge websockets by pinging them to be sure they are still online
    # - check for users logged in ...
    #
