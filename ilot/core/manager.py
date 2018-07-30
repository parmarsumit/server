'''
Created on 25 janv. 2016

@author: nicolas
'''
from datetime import datetime
import sys
import threading
import uuid
import os
import time

from ilot.core.parsers.api_json import load_json, dump_json

from pytz import timezone
import pytz
utc = pytz.utc
#eastern = timezone('US/Eastern')

global _core
_core = None


class Core(dict):
    templates = {}
    def __getitem__(self, key):
        return self.templates[key]
    def __contains__(self, key):
        return self.templates.__contains__(key)

class AppManager():

    _core = None
    #_core_lock = threading.Lock()

    organization_by_host = {}
    host_by_organization = {}

    _sections = []
    sections = []

    actions = []

    properties_by_action = {}
    class_by_action = {}
    instance_by_action = {}

    registred_classes = []

    sections_cache = {}

    @classmethod
    def get_core(cls):
        #from rux.core.manager import CoreManager
        # return CoreManager.get_core()
        #with cls._core_lock:
        if cls._core == None:
            #from core.models import DataPath
            #cls._core = Core(DataPath)
            cls._core = Core()
        return cls._core

    @staticmethod
    def register_class(cls, actions):
        AppManager.register_actions(actions)

        if not cls in AppManager.registred_classes:
            AppManager.registred_classes.append(cls)

        for action in actions:
            AppManager.class_by_action[action] = cls

    @staticmethod
    def process_action(request, action, input_data, **kwargs):
        action_class = AppManager.class_by_action[action]
        if not action in AppManager.instance_by_action:
            action_instance = action_class()
            AppManager.instance_by_action[action] = action_instance
            #action_instance.get_actions()
        else:
            action_instance = AppManager.instance_by_action[action]
        kwargs['action'] = action
        response = action_instance.pre_process(request, input_data, **kwargs)

        return response

    @staticmethod
    def register_section(cls):
        cls.get_actions()
        if not cls.view_name in AppManager._sections:
            AppManager._sections.append(cls.view_name)
            class_actions = []
            for action in cls.class_actions:

                action_label = cls.class_actions_labels.get(action, action)
                class_actions.append( (action, action_label) )

                AppManager.properties_by_action[action] = {
                    'action':action,
                    'action_label':action_label,
                    'section':cls.view_name,
                    'section_label':cls.view_title
                }

            AppManager.sections.append((cls.view_name, cls.view_title, cls.default_action, class_actions))



    @staticmethod
    def register_actions(actions):
        for action in actions:
            if not action in AppManager.actions:
                AppManager.actions.append(action)


    @staticmethod
    def get_actions():
        return AppManager.actions

    @staticmethod
    def get_sections(profile, item):
        from ilot.core.models import request_switch
        from ilot.models import has_perm

        s_key = profile.akey+request_switch.organization.id

        if s_key in AppManager.sections_cache:
            return AppManager.sections_cache[s_key]

        #return None
        sections = []
        if profile:
            #organization_item = request_switch.organization.get_item()

            # check for permissions
            for section in AppManager.sections:
                section_actions = []
                section_words = []
                for action, action_label in section[3]:
                    if profile and has_perm(action, request_switch.organization, profile, item):
                        section_actions.append((action, action_label))
                        section_words.append(action)
                if len(section_actions):
                    if len(section_actions) == 1:
                        profile_section = (section[0], section_actions[0][1], section_actions[0][0], section_actions, section_words)
                    else:
                        profile_section = (section[0], section[1], section[2], section_actions, section_words)
                    sections.append(profile_section)
            AppManager.sections_cache[s_key] = sections
            return sections
        else:
            return AppManager.sections



    @staticmethod
    def get_action_properties(action):
        if action in AppManager.properties_by_action:
            return AppManager.properties_by_action[action]
        else:
            return {'action':action,
                    'action_label':action,
                    'section':'',
                    'section_label':''}

    @staticmethod
    def get_new_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def get_ref_time():
        return int(time.time()*100000)

    @staticmethod
    def get_valid_time():
        return utc.localize(datetime.utcnow())

    #statuses = ['indexed', 'drafted', 'initialized', 'rewarded', 'budgeted', 'assigned', 'calling']
    #actions = ['index', 'view', ]
    #ntypes = ['Project', 'Initiator', 'Contribution', 'RewardedContribution', 'Initiative']
    #attributes = ['value', 'amount', ]
    #methods = ['total',]

    actions_list = []
    statuses_list = []
    types_list = []
    attributes_list = []
    __cached_lists = False

    @staticmethod
    def cache_lists():
        if AppManager.__cached_lists:
            return
        from ilot.rules.models import Action, Status, Type, Attribute
        AppManager.actions_list = list(Action.objects.select_related().all().values_list('name', flat=True).distinct())
        AppManager.statuses_list = list(Status.objects.select_related().all().values_list('name', flat=True).distinct())
        AppManager.types_list = list(Type.objects.select_related().all().values_list('name', flat=True).distinct())
        AppManager.attributes_list = list(Attribute.objects.select_related().all().values_list('name', flat=True).distinct())
        AppManager.__cached_lists = True

    @staticmethod
    def get_release():
        return Release.objects.all().order_by('-ref_time')[0]
