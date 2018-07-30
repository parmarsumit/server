'''
Created on 16 mai 2014

@author: rux
'''
import copy
import traceback
import uuid

from django.contrib import messages
from django.core.cache import cache as action_cache
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from django.utils.translation import get_language
import six
from django.db.models import ObjectDoesNotExist

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.base import Template

from ilot.core.models import DataPath, Item, request_switch
from ilot.core.parsers.api_json import load_json, dump_json
from ilot.core.views.action import ActionView
import hashlib
from django.core.paginator import Paginator
from django.db.models.query_utils import Q
from django.core.exceptions import PermissionDenied

from ilot.core.manager import AppManager

from django.forms import ValidationError

from django.contrib.auth import get_user_model, login, authenticate

import logging
logger = logging.getLogger(__name__)

from django.conf import settings

import mimetypes
import os

try:
    from functools import reduce
except:
    pass
import operator


from ilot.core.models import get_locale_as_organization
from ilot.rules.models import Action

__all__ = ['ActionPipeView', ]


class ActionPipeView(ActionView):
    '''
    base class for an action pipe view
    '''

    """
    Default action data dict
    """
    pipe_data_model = {
        # hash_key
        'akey': 'default',
        # range key
        'action': 'undefined', #-> status !
        # second range index
        'data': dump_json({}),
    }

    pipe_hash_key = 'akey'
    #pipe_range_key = 'action'
    pipe_range_key = 'context'


    def __init__(self, *args, **kwargs):
        return super(ActionPipeView, self).__init__(*args, **kwargs)

    @classmethod
    def get_new_session_user_key(self):
        return str(uuid.uuid4())

    @classmethod
    def get_request_akey(cls, request):
        """
        Get actionpipe data container key
        Generates a new one if missing cookie
        """
        akey = None
        if cls.pipe_hash_key in request.session:
            akey = request.session[cls.pipe_hash_key]

        if not akey:
            akey = AppManager.get_new_uuid()
            request.session[cls.pipe_hash_key] = akey
        return akey

    def get_session_user_keys(self, request):
        """
        Get actionpipe data container key
        Generates a new one if missing cookie
        """
        return ActionPipeView.get_request_akey(request)


    def get_default_pipe_data(self, request, akey, **kwargs):
        """
        Get a default action data dict
        """
        pipe_data = copy.deepcopy(self.pipe_data_model)

        pipe_data['akey'] = akey
        pipe_data['context'] = kwargs['context']
        #pipe_data['target'] = akey
        pipe_data['action'] = kwargs.get('action')
        pipe_data['locale'] = get_locale_as_organization()
        pipe_data['data'] = {}
        return pipe_data

    def get_user_profile(self, request, **kwargs):
        akey = self.get_session_user_keys(request)
        return DataPath(**self.update_actionpipe_data(request, {}, akey, **kwargs))

    def get_context_dict(self, request, user_profile, input_data, **kwargs):
        template_args = super(ActionPipeView, self).get_context_dict(request, user_profile, input_data, **kwargs)
        template_args['currentNode'] = kwargs['node']
        return template_args


    def pre_process(self, request, input_data, **kwargs):
        """
        Hook before processing the request
        Best place to make user/objects rights management
        """
        akey = self.get_session_user_keys(request)

        kwargs['pipe'] = self.update_actionpipe_data(request, input_data, akey, **kwargs)

        return super(ActionPipeView, self).pre_process(request, input_data, **kwargs)

    def process(self, request, user_profile, input_data, template_args, **kwargs):
        return self.manage_pipe(request, user_profile, input_data, template_args, **kwargs)

    def manage_pipe(self, request, user_profile, input_data, template_args, **kwargs):

        action = kwargs['action']

        if not kwargs.get('trigger'):
            kwargs['trigger'] = None

        if kwargs['do'] == False:
            bound_forms = False
            managed_data = input_data
        else:
            bound_forms = True
            managed_data = input_data

        instances = self.get_forms_instances(action,
                                             user_profile,
                                             input_data,
                                             kwargs)

        action_forms = self.get_validated_forms( instances,
                                                 managed_data,
                                                 action,
                                                 save_forms=False,
                                                 bound_forms=bound_forms,
                                                 files=request.FILES,
                                                 )

        template_args['action_forms'] = action_forms
        action_data = kwargs['pipe']

        #template_args['notifs'] = self.update_feed().order_by('-ref_time')

        # check for form validity
        if bound_forms and self.validate_action_forms(request, action_forms):

            # check id there is an authorization to produce
            action_item = action_forms[0].action_item
            new_origin = action_forms[0].instance

            for f in action_forms:
                f.full_clean()

            #print('AUTHORIZING ?', action_item.authorize, action_item.name)

            if action_item.authorize and not kwargs.get('token'):

                payload = {}
                for f in action_forms:
                    payload.update(f.get_data())

                #if not kwargs['origin']._state.db and not kwargs['origin']._saved:
                #    kwargs['origin'].save()

                print('AUTHORIZING ', kwargs['origin'])

                authorization = self.authorize_behavior(kwargs['origin'], new_origin, action_forms[0].action_item, payload)

                #new_origin.get_data()
                #new_origin._data.update(payload)

                template_args['origin'] = new_origin
                template_args['node'] = new_origin.related

                kwargs['action_item'] = f.action_item

                kwargs['authorization'] = authorization

                template_args = self.manage_action_completed(request, user_profile, template_args, input_data, **kwargs)
            else:
                # save if all valids, no need to authorize, or have a valid token
                if not action_item.authorize or kwargs.get('token'):
                    for f in action_forms:
                        f.__authorize__ = True
                        f.save()

                    #del kwargs['token']

                if f.action_item.meta_type != 'request':
                    # handle triggers
                    try:
                        for trigger in action_item.triggers.filter(
                                Q(type__in=kwargs['origin'].get_infered_types(replace=False))
                                | Q(type__in=kwargs['node'].get_infered_types(replace=False))
                            ).order_by('order'):

                            self.dispatch_trigger(request, input_data, trigger, new_origin, {})

                        template_args['origin'] = new_origin
                        template_args['node'] = new_origin.related

                        kwargs['action_item'] = f.action_item

                        template_args = self.manage_action_completed(request, user_profile, template_args, input_data, **kwargs)

                    except ValidationError as e:
                        messages.warning(request, e)
                        raise PermissionDenied
        else:
            if bound_forms and kwargs['trigger']:
                print('INVALID FORM in pipe', kwargs['trigger'])
                raise ValidationError( 'Something gone wrong during '+action_forms[0].action_item.name)

        if not kwargs['trigger']:
            return self.render(request, template_args, **kwargs)
        else:
            print('SKIPING RENDER ')
            return None


    def authorize_behavior(self, origin, event, action_item, payload):
        '''
        Create an authorization link
        '''
        #
        from ilot.models import Authorization

        origin_key = origin.id
        target_akey = event.target

        #if action_item.meta_type == 'actor':
        #    target_akey = event.id

            # origin_key = event.id
        #    print('AUTHORIZTION TARGETING ACTOR ', event.id)
        #else:
        #    print('AUTHORIZATION ', event.target)

        authorization = Authorization(organization=request_switch.organization,
                                      origin=origin_key,
                                      action=action_item.behavior.name,
                                      akey=target_akey,
                                      payload=dump_json(payload))
        authorization.save()

        # event.behavior = action_item.behavior.name

        #print('AUTHO', 'O', origin.id, 'A', origin.target, 'E', event.id, 'B', event.behavior)

        return authorization


    def manage_action_completed(self, request, user_profile, template_args, final_data, **kwargs):
        """
        Handles action completion
        """
        action_item = kwargs['action_item']
        action = kwargs['action']
        #self.save_actionpipe_data(request, final_data, final_data['akey'], **kwargs)
        template_args['action_forms'] = self.get_validated_forms(self.get_forms_instances(action,
                                                                 user_profile,
                                                                 {},
                                                                 kwargs),
                                                                 {},
                                                                 action,
                                                                 save_forms=False,
                                                                 bound_forms=False,
                                                                 )
        # notify
        if not action_item.authorize or kwargs.get('token'):
            template_args['action_is_done'] = True
        else:
            template_args['action_is_pending'] = True
            #notifications = Notification.objects.filter(status__name=template_args['origin'].status,
            #                            type__in=kwargs['origin'].get_infered_types())
            if action_item.webhook:
                request = action_item.webhook.parse(user_profile.akey, template_args['origin'], authorization=kwargs['authorization'])
                request.dispatch()
            else:
                template_args['authorization'] = kwargs['authorization']

            template_args['origin'] = kwargs['origin']

        return template_args

    def update_feed(self):

        # get all my roles
        # from these roles get all types it applies todo
        # from thee get all the rules and the status from these

        from ilot.rules.models import Type
        from ilot.core.models import Moderation, Item
        from ilot.grammar.models import Notification
        akey = request_switch.akey
        actor = Item.objects.get_at_id(akey)
        return actor.do_query('all_notifications')
        # get all my roles
        akey = request_switch.akey

        interacted_actor = Moderation.objects.filter( Q(akey=akey) )
        interacted_target = Moderation.objects.filter( Q(target=akey) )

        interacted_actor_statuses = interacted_actor.values_list('status', flat=True)
        interacted_target_statuses = interacted_target.values_list('status', flat=True)

        my_roles = Type.objects.filter( Q(status__name__in=interacted_actor_statuses, reference='actor') |
                                        Q(status__name__in=interacted_target_statuses, reference='target') )

        my_notif_rules = Notification.objects.filter(target__in=my_roles)

        # for all my notif rules, collect the events i should be notified of
        actor = Item.objects.get_at_id(akey)
        my_contexts = []
        for rule in my_notif_rules:

            #typed = actor.do_query('query_all_'+rule.type.name).values_list('id', flat=True)
            #roled = actor.do_query('query_all_'+rule.target.name+'_items').values_list('id', flat=True)

            if rule.target.reference == 'target':

                if rule.target.type.reference == 'event':
                    roles = Moderation.objects.filter(status=rule.target.status.name,
                                                      target=akey).distinct()
                else:
                    roles = Moderation.objects.filter(status=rule.target.status.name,
                                                      target=akey,
                                                      related__events__status=rule.target.type.status.name).distinct()

            elif rule.target.reference == 'actor':

                if rule.target.type.reference == 'event':
                    roles = Moderation.objects.filter(status=rule.target.status.name,
                                                      akey=akey).distinct()
                else:
                    roles = Moderation.objects.filter(status=rule.target.status.name,
                                                      akey=akey,
                                                      related__events__status=rule.target.type.status.name).distinct()

            #if rule.type.reference == 'event':
            if rule.type.type.reference == 'event':
                types = Moderation.objects.filter(status=rule.type.status.name,
                                                  origin__status=rule.type.type.status.name).distinct()
            else:
                types = Moderation.objects.filter(status=rule.type.status.name,
                                                  related__events__status=rule.type.type.status.name).distinct()


            #elif rule.type.reference == 'related':
            #    types = Moderation.objects.filter(status=rule.type.status.name,
            #                                      related__events__status=rule.type.type.status.name).distinct()


            if rule.target.scope == 'descendants':
                types = Moderation.objects.filter( context__in=roles.values_list('context', flat=True).distinct() )
                roles = Moderation.objects.filter( context__in=roles.values_list('context', flat=True).distinct() )


            if rule.type.reference == 'event':
                my_contexts.append( Q(origin__in=types,
                                      origin__related__events__in=roles,
                                      status=rule.status.name, ) )

            elif rule.type.reference == 'related' or rule.type.reference == 'context':
                my_contexts.append( Q(related__events__in=types,
                                      origin__related__events__in=roles,
                                      status=rule.status.name, ) )

            if True == False:

                if rule.target.reference == 'target':

                    if rule.target.scope == 'descendants':
                        origins = Moderation.objects.filter(context__in=roles.values_list('context', flat=True).distinct())
                        print('CONTEXTS', origins.values_list('context', flat=True).distinct())

                    if rule.type.reference == 'event':
                        my_contexts.append( Q(origin__origin__status=rule.type.status.name,
                                              origin__related__events__in=roles,
                                              status=rule.status.name, ) )

                    elif rule.type.reference == 'related':
                        my_contexts.append( Q(related__events__status=rule.type.status.name,
                                              origin__related__events__in=roles,
                                              status=rule.status.name, ) )

                    elif rule.type.reference == 'context':
                        my_contexts.append( Q(related__events__status=rule.type.status.name,
                                              origin__related__events__in=roles,
                                              status=rule.status.name, ) )
                    else:
                        print('NOTIF REF ?', rule.type.reference, rule)
                        pass
                        if True==False:
                            my_contexts.append( Q(related_id__in=typed,
                                                  related__events__status=rule.target.status.name,
                                                  origin_id__in=roled,
                                                  origin__target=akey,
                                                  status=rule.status.name, ) )

                elif rule.target.reference == 'actor':

                    origins = Moderation.objects.filter(status=rule.target.status.name,
                                                        akey=akey,
                                                        related__events__status=rule.target.type.status.name)

                    if rule.target.scope == 'descendants':
                        origins = Moderation.objects.filter(context__in=origins.values_list('context', flat=True))

                    if rule.type.reference == 'event':
                        my_contexts.append( Q(origin__origin__status=rule.type.status.name,
                                              origin__related__events__in=origins,
                                              status=rule.status.name, ) )

                    elif rule.type.reference == 'related':
                        my_contexts.append( Q(related__events__status=rule.type.status.name,
                                              origin__related__events__in=origins,
                                              status=rule.status.name, ) )

                    elif rule.type.reference == 'context':
                        my_contexts.append( Q(related__events__status=rule.type.status.name,
                                              origin__related__events__in=origins,
                                              status=rule.status.name, ) )
                    else:
                        pass
                else:
                    print('NOTIF TARGET REF ?', rule.target.reference, rule)

        if len(my_contexts):
            maybe_notified = Moderation.objects.filter( Q(reduce(operator.or_, my_contexts)) ).distinct()
        else:
            return Moderation.objects.none()

        print(len(maybe_notified), 'NOTIF')

        return maybe_notified


        my_notif_statuses = my_notif_rules.values_list('status__name', flat=True)


        object_types = my_notif_rules.values_list('type', flat=True)

        print(len(my_roles), 'MY ROLES', my_roles)
        print(len(object_types), 'LISTENING TYPES', object_types)

        listening_statuses = Type.objects.filter(id__in=object_types).values_list('status__name')

        maybe_notified = Moderation.objects.filter(origin__status__in=listening_statuses, status__in=my_notif_statuses)
        print(len(maybe_notified), 'MAYBE NOTIF')

        # filter these with roled
        my_contexts = []
        target_roles = my_roles.filter(reference='target')
        my_contexts.append( Q(target=akey,
                              status__in=target_roles.values_list('status__name', flat=True),
                              related__status__in=target_roles.values_list('type__status__name', flat=True)) )

        actor_roles = my_roles.filter(reference='actor')

        my_contexts.append( Q(akey=akey,
                              status__in=actor_roles.values_list('status__name', flat=True),
                              related__status__in=actor_roles.values_list('type__status__name', flat=True)) )

        print(target_roles, len(my_contexts), 'CONTEXTS')

        maybe_notified = maybe_notified.filter( my_contexts[0] | my_contexts[1] )

        #

        # and items ?
        print(len(maybe_notified), 'NOTIF')

        return maybe_notified


    def dispatch_trigger(self, request, input_data, trigger, new_origin, template_args):

        from ilot.rules.models import Trigger

        # print('DISPATCHING', trigger, ' on ', new_origin.get_infered_types(), '\n\n')
        # execute triggers if they pass condition
        if trigger.condition:
            if not trigger.condition.is_true(new_origin):
                print(trigger, 'FAILED TRIGGER CONDITION ', trigger.condition)
                return template_args

        #trigger_data = load_json(trigger.data)
        trigger_data = input_data

        if not trigger.actor_type:
            #print('MUST DEFINE ACTOR ')
            trigger_actor = new_origin.akey
        else:
            trigger_actor = new_origin.get_actor_by_type(trigger.actor_type)

        if not trigger.target_type:
            #print('MUST DEFINE TARGET ')
            trigger_target = new_origin.target
        else:
            trigger_target = new_origin.get_actor_by_type(trigger.target_type)

        trigger_kwargs = {
            'do':True,
            'ext':'',
            'action':trigger.behavior.name,
            'path': new_origin.id,
            'context': new_origin.context,
            'node': new_origin.related,
            'origin': new_origin,
            'target':trigger_target,
            'trigger':trigger,
        }
        trigger_pipe = self.update_actionpipe_data(request, trigger_data, trigger_actor, **trigger_kwargs)
        trigger_profile = DataPath(**trigger_pipe)
        trigger_kwargs['pipe'] = trigger_pipe

        #print('DOING TRIGGER ', trigger_pipe, trigger_kwargs)
        try:
            template_args = self.manage_pipe(request, trigger_profile, trigger_data, template_args, **trigger_kwargs)
        except:
            traceback.print_exc()
            raise ValidationError('OOps, looks like something gone wrong in '+trigger.name)

        return template_args

        #print('\n\nDONE TRIGGER ', trigger)
        #messages.success(request, 'Great ! done the trigger !'+trigger.name)



    def render(self, request, template_args, **kwargs):
        """
        Render depending on the request and node
        """
        if kwargs['ext'] in ('', '/'):
            template_ext = '.html'
        else:
            template_ext = kwargs['ext']

        template_args['messages'] = []

        from django.contrib.messages import get_messages
        storage = get_messages(request)

        for message in storage:
            template_args['messages'].append(message)

        if request.path in ('', '/') and not kwargs.get('template') and request_switch.interface:
            t = Template(request_switch.interface.content)
            template_ext = '.html'
            context = RequestContext(request, template_args)
            return HttpResponse(t.render(context), content_type=mimetypes.guess_type('filename'+template_ext)[0])
        else:
            from django.template import loader
            t = loader.select_template((kwargs.get('template', 'actions/'+kwargs['action']+template_ext), '200'+template_ext, 'ilot/200'+template_ext))

            return HttpResponse(t.render(template_args, request), content_type=mimetypes.guess_type('filename'+template_ext)[0])



    def deliver(self, request, response, **kwargs):
        '''
        Sets final touch to request
        '''
        return super(ActionPipeView, self).deliver(request, response, **kwargs)


    def update_actionpipe_data(self, request, data, akey, **kwargs):
        """
        Update the action pipe data with provided dict
        Ensures clean and freshness of the pipe_data dict
        """
        #data_dict = self.get_latest(akey, kwargs['path'], kwargs['action'])
        #if data_dict is None:
        data_dict = self.get_default_pipe_data(request, akey, **kwargs)

        # update dict with new values
        for k in data:
            data_dict['data'][k] = data[k]

        # clean empty fields
        fields = list(data_dict['data'].keys())
        for field in fields:
            if not data_dict['data'][field]:
                del data_dict['data'][field]
        data_dict['action'] = kwargs.get('action')
        data_dict['context'] = kwargs['context']
        data_dict['locale'] = get_locale_as_organization()
        data_dict['ref_time'] = DataPath.get_ref_time()
        return data_dict


    def save_actionpipe_data(self, request, data_dict, akey, **kwargs):
        '''
        DEPRECATED

        Saves it to nosql
        This is an "atomic" operation,
        you should not try to save data another way
        because of cache handling
        '''
        # compress
        range_key = data_dict[self.pipe_range_key]
        data_dict['data'] = dump_json(data_dict['data'])
        self.put_action(akey, range_key, data_dict)
        return data_dict


    hash_key = 'akey'
    #range_key = 'action'
    range_key = 'context'

    def put_action(self, hash_key, range_key, data):
        '''
        DEPRECATED
        '''

        try:
            params = {}
            params[self.hash_key] = hash_key
            params[self.range_key] = range_key
            #data_object = self.model.objects.filter(**params).order_by('-ref_time')[:1][0]
            data_object = DataPath.objects.filter(akey=hash_key, context=range_key, locale=get_locale_as_organization(), action=data['action']).order_by('-ref_time')[:1][0]

            for key in data.keys():
                if key == 'data':
                    #data_object.__setattr__(key, dump_json(data[key]))
                    data_object.set_data(data[key])
                #else:
                data_object.__setattr__(key, data[key])

            data_object.full_clean()
            data_object.save()

        except IndexError:

            if not self.range_key in data:
                data[self.range_key] = range_key

            data_keys = data.keys()
            for key in data_keys:
                if key.endswith('_ptr'):
                    del data[key]

            new_object = DataPath(**data)

            # should check for matching hash_key/range_key
            new_object.akey = hash_key
            new_object.context = range_key
            new_object.action = data['action']
            new_object.locale = get_locale_as_organization()

            new_object.full_clean()
            new_object.save()

    def get_latest(self, hash_key, range_key, action):
        '''
        DEPRECATED
        '''

        try:
            data_obj = DataPath.objects.filter(akey=hash_key, context=range_key, locale=get_locale_as_organization(), action=action).order_by('-ref_time')[:1][0]

            pipe_data = {}
            obj_data = model_to_dict(data_obj)
            pipe_data.update(obj_data)
            pipe_data['data'] = data_obj.get_data()

                #pipe_data['data'] = load_json(obj_data['data'])

            #try:
            #    pipe_data['data'] = json.loads(data_obj.data)
            #except:
            #    traceback.print_exc()
            #    pipe_data['data'] = {}
            #pipe_data['data'] = deepcopy(data_obj.data)
            #pipe_data['ref_time'] = AppManager.get_ref_time()

            return pipe_data

        except IndexError:
            return None
