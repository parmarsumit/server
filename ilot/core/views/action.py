'''
Created on 24 oct. 2013

@author: rux
'''
from ilot.core.forms.base import BaseActionForm
from ilot.core.parsers.api_json import API_json_parser, load_json
import hashlib
import inspect
import logging
import re

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, resolve
from django.forms.models import model_to_dict, ModelForm
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from django.views.generic.base import View

from ilot.core.models import Moderation, Item, Translation, DataPath

from ilot.rules.models import Action

logger = logging.getLogger(__name__)

from ilot.core.models import object_tree_cache, request_switch
from ilot.core.manager import AppManager

from django.db.models import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class ActionView(APIView):
    """
    The default base view for all views
    implementing a parser
    and a documentation
    """
    __version__ = "0.5"

    view_name = 'core'
    view_title = 'Core'
    view_template = 'core/base.html'

    default_action = 'view'

    class_actions = []
    class_actions_forms = {'view': []}
    class_action_templates = {}
    class_actions_labels = {'view':'Afficher'}
    class_actions_statuses = {'view': [('view', 'viewed')]}

    json_parser = API_json_parser

    permission_classes = (AllowAny,)

    def __init__(self, *args, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # initialise the default view behavior here
        # register view_name over a global variable
        super(ActionView, self).__init__(*args, **kwargs)
        self.__class__.get_actions()
        for action in self.__class__.actions:
            AppManager.instance_by_action[action] = self

    @classmethod
    def get_actions(cls):
        class_stack = inspect.getmro(cls)[::-1]

        actions = []
        actions_forms = {}
        action_templates = {}

        for base_class in class_stack:

            check_classes = inspect.getmro(base_class)

            if ActionView in check_classes:
                #
                if not 'actions' in cls.__dict__:
                    if 'class_actions' in base_class.__dict__:
                        for action in base_class.class_actions:
                            if action not in actions:
                                actions.append(action)
                #
                if not 'actions_forms' in cls.__dict__:
                    if 'class_actions_forms' in base_class.__dict__:
                        for action in base_class.class_actions_forms:
                            actions_forms[action] = base_class.class_actions_forms[action]
                #
                if not 'action_templates' in cls.__dict__:
                    if 'class_action_templates' in base_class.__dict__:
                        for action in base_class.class_action_templates:
                            action_templates[action] = base_class.class_action_templates[action]

        if not 'actions' in cls.__dict__:
            cls.actions = actions
        if not 'actions_forms' in cls.__dict__:
            cls.actions_forms = actions_forms
        if not 'action_templates' in cls.__dict__:
            cls.action_templates = action_templates

        #AppManager.register_actions(cls.actions)
        AppManager.register_class(cls, cls.actions)
        return cls.actions


    @classmethod
    def get_url_regexp(cls, base_path=None, trailing_cap=None):
        """
        Returns a multi-format and multi-action url regexp string for this view
        """
        action_list = cls.get_actions()
        cls_actions = []

        for a in action_list:
            cls_actions.append(a.replace('_', '\_'))

        cls_actions = sorted(cls_actions, key=lambda item: len(cls_actions)-len(item))

        url_regexp = ''

        if base_path:
            url_regexp += base_path

        url_regexp += '(?P<action>('
        url_regexp += '|'.join(cls_actions)
        url_regexp += '|){1})'

        return url_regexp


    def get(self, request, *args, **kwargs):
        """
        Manage a GET request
        """
        object_tree_cache.purge()
        if kwargs.get('action') in ('', None):
            kwargs['action'] = self.default_action
        reverse_keys = []
        for key in kwargs:
            reverse_keys.append(key)
        kwargs['reverse_keys'] = reverse_keys
        kwargs['args'] = args
        kwargs['view_name'] = resolve(request.path_info).url_name

        # parse input data
        input_data = self.get_input_data(request, **kwargs)
        if not 'do' in input_data:
            kwargs['do'] = False
        else:
            kwargs['do'] = input_data['do']

        # start preprocessing the request
        return self.pre_process(request, input_data, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Manage a POST request
        """
        object_tree_cache.purge()
        if kwargs.get('action') in ('', None):
            kwargs['action'] = self.default_action
        reverse_keys = []
        for key in kwargs:
            reverse_keys.append(key)
        kwargs['reverse_keys'] = reverse_keys
        kwargs['args'] = args
        kwargs['view_name'] = resolve(request.path_info).url_name
        # parse input data
        input_data = self.get_input_data(request, **kwargs)
        if not 'do' in input_data:
            #input_data['do'] = True
            kwargs['do'] = True
        else:
            kwargs['do'] = input_data['do']
        # start preprocessing the request
        return self.pre_process(request, input_data, **kwargs)

    def get_referer_path(self, request):
        """
        Get a clean referer path to the request object
        """

        # if the user typed the url directly in the browser's address bar
        referer = request.META.get('HTTP_REFERER')
        if not referer:
            return request.path
        else:
            return referer
        # remove the protocol and split the url at the slashes
        referer = re.sub('^https?:\/\/', '', referer).split('/')
        if referer[0] != request.META.get('SERVER_NAME'):
            return '/'+request.path

        # add the slash at the relative path's view and finished
        referer = u'/' + u'/'.join(referer[1:])
        return referer


    def get_user_profile(self, request, **kwargs):
        """
        Retreive user profile from the request user
        """
        return {}

    def get_context_dict(self, request, user_profile, input_data, **kwargs):
        template_args = {}
        template_args['request'] = request
        template_args['user_profile'] = user_profile
        template_args['input_data'] = input_data
        template_args['pipe_data'] = kwargs.get('pipe', {})
        template_args['action'] = kwargs.get('action')
        return template_args

    def get_input_data(self, request, **kwargs):
        """
        Get a dict of all the inputs merged ( GET < POST|json )

        The GET query keys are appended and updated
        by either the POST or the json['payload'] query keys

        You can change this behavior by overwritting this method in your view
        """
        data = {}

        # use the get variables first or last ?
        data.update(request.GET.dict())

        # use either the post or json data ?
        if 'application/json' in request.META.get('CONTENT_TYPE', ''):
            data.update(load_json(request.body))
        else:
            data.update(request.POST.dict())

        # remove csrftoken
        if 'csrfmiddlewaretoken' in data:
            del data['csrfmiddlewaretoken']

        return data

    def get_forms_instances(self, action, user_profile, input_data, kwargs):
        """
        Reteive the context
        """
        try:
            self.action_item = Action.objects.get(name=action)
        except ObjectDoesNotExist:
            self.action_item = Action(name=action,)

        # target may be set upstream by a trigger
        # otherwise, it must come from the action setup
        # it may be selected by the user or coming from infered types targets
        if 'target' in kwargs:
            target = kwargs['target']
        else:
            if input_data.get('target'):
                try:
                    Item.objects.get_at_id(input_data.get('target'))
                    target = input_data.get('target')
                except:
                    target = user_profile.akey
            else:
                target = user_profile.akey
        
        status_name = self.action_item.status.name

        #
        if self.action_item.meta_type == 'context':
            """
            Create a new item context
            """
            instance = Item(id=user_profile.id,
                            related_id=user_profile.id,
                            parent=None,
                            origin_id=kwargs['origin'].id,
                            target=target,
                            status=status_name,
                            **kwargs['pipe'])
            instance.context = user_profile.id

        elif self.action_item.meta_type == 'actor':
            """
            Create a new actor item
            """
            instance = Item(id=user_profile.id,
                            related_id=user_profile.id,
                            parent=None,
                            origin_id=user_profile.id,
                            target=user_profile.id,
                            status=status_name,
                            **kwargs['pipe'])

            instance.akey = user_profile.id
            instance.origin_id = user_profile.id
            instance.context = user_profile.id
            instance.target = user_profile.id

        elif self.action_item.meta_type == 'item':
            """
            Create a new item
            """
            instance = Item(id=user_profile.id,
                            related_id=user_profile.id,
                            parent=kwargs['node'],
                            origin_id=kwargs['origin'].id,
                            target=target,
                            status=status_name,
                            **kwargs['pipe'])

        elif self.action_item.meta_type == 'clone':
            """
            We clone the item and it's data to a new one
            TOCARE
            If origin_id is a version of the item,
            then we will use it's state to create the new one
            """
            item_data = kwargs['node'].get_data()

            instance = Item(id=user_profile.id,
                            related_id=user_profile.id,
                            parent=kwargs['node'].parent,
                            origin_id=kwargs['origin'].id,
                            target=target,
                            status=status_name,
                            **kwargs['pipe'])

            #for datablock in self.get_data():
            #instance.title = kwargs['node'].title
            #instance.slug = kwargs['node'].slug
            #instance.label = kwargs['node'].label
            #instance.description = kwargs['node'].description
            #instance.type = kwargs['node'].type

            instance.start = kwargs['node'].start
            instance.end = kwargs['node'].end

            #instance.set_data(item_data)

            print('Cloning ...')

        elif self.action_item.meta_type == 'event':
            instance = Moderation(id=user_profile.id,
                                    related_id=kwargs['node'].id,
                                    origin_id=kwargs['origin'].id,
                                    target=target,
                                    status=status_name,
                                    **kwargs['pipe'])

        elif self.action_item.meta_type == 'version':
            instance = Translation(id=user_profile.id,
                                    related_id=kwargs['node'].id,
                                    origin_id=kwargs['origin'].id,
                                    target=target,
                                    status=status_name,
                                    **kwargs['pipe'])

            # buffer item data
            instance._data = kwargs['node'].get_data()

            #instance.set_data(kwargs['node'].get_data())

        else:
            instance = DataPath(id=user_profile.id, **kwargs['pipe'])

        return (instance,)


    def get_forms_data(self, *forms):
        """
        Get a data dictionnary of the provided forms instances fields data
        """
        data = {}
        for form in forms:
            data.update(form.get_data())

        return data

    def get_action_forms(self, action):
        """
        Returns a tuple with the list of forms invovlved
        """

        if self.action_item.meta_type == 'context':
            class ActionForm(BaseActionForm):
                class Meta:
                    model = Item
                    fields = []
        elif self.action_item.meta_type == 'actor':
            class ActionForm(BaseActionForm):
                class Meta:
                    model = Item
                    fields = []
        elif self.action_item.meta_type == 'item':
            class ActionForm(BaseActionForm):
                class Meta:
                    model = Item
                    fields = []
        elif self.action_item.meta_type == 'clone':
            class ActionForm(BaseActionForm):
                class Meta:
                    model = Item
                    fields = []
        elif self.action_item.meta_type == 'event':
            class ActionForm(BaseActionForm):
                class Meta:
                    model = Moderation
                    fields = []
        elif self.action_item.meta_type == 'version':
            class ActionForm(BaseActionForm):
                class Meta:
                    model = Translation
                    fields = []
        else:
            class ActionForm(BaseActionForm):
                class Meta:
                    model = DataPath
                    fields = []

        return (ActionForm,)

        forms = tuple()

        if action in self.actions_forms:
            aforms = self.actions_forms[action]
        else:
            aforms = []

        for form_class in aforms:
            forms += (form_class,)

        return forms

    def get_validated_forms(self, form_models,
                            input_data, action,
                            save_forms=False, files=None, bound_forms=True):
        """
        From a tuple of model instances,
        get the corresponding action forms
        You can save them manually by passing False to save_forms
        """
        if files is None:
            files = {}
        forms = tuple()

        if action in self.actions_forms:
            aforms = self.actions_forms[action]
        else:
            aforms = []

        aforms = self.get_action_forms(action)
        #print(form_models, aforms)
        instances = []

        if form_models:
            for form_class in aforms:
                for model_instance in form_models:

                    if (model_instance, form_class) in instances:
                        continue

                    if issubclass(form_class, BaseActionForm) and \
                        isinstance(model_instance, form_class.Meta.model) and \
                        model_instance.__class__.__name__ == form_class.Meta.model.__name__:

                        form_data = model_to_dict(model_instance, exclude=('translation_ptr',
                                                                           'moderation_ptr',
                                                                           'datapath_ptr',
                                                                           'target'
                                                                            ))
                        #del model_data['target']
                        model_data = model_instance.get_data()
                        #print(model_data, 'FORM', form_data, 'INPUT', input_data)
                        form_data.update(model_data)
                        form_data.update(input_data)

                        form_data['target'] = input_data.get('target', '')

                        if bound_forms:
                            form_instance = form_class(action, form_data,
                                                       instance=model_instance,
                                                       files=files)
                        else:
                            form_instance = form_class(action, initial=form_data, instance=model_instance)

                        if bound_forms and save_forms and form_instance.is_valid():
                            form_instance.full_clean()
                            form_instance.save()

                        instances.append((model_instance, form_class))

                        forms += (form_instance,)

        old_forms = False
        if old_forms:
            for form_class in aforms:
                if issubclass(form_class, ActionPipeForm):
                    if bound_forms:
                        form_instance = form_class(input_data)
                    else:
                        form_instance = form_class(initial=input_data)
                    if bound_forms and save_forms and form_instance.is_valid():
                        if issubclass(form_class, ModelForm):
                            form_instance.save()
                    forms += (form_instance,)

        if save_forms:
            for instance in instances:
                instance.full_clean()
                instance.save()

        return forms


    def validate_action_forms(self, request, forms):
        '''
        Validates a given list of forms
        and adds validation error message to request
        '''
        if not len(forms):
            return False

        all_forms_valid = True
        for f in forms:

            if f.is_bound == False:
                all_forms_valid = False

            f.full_clean()
            if not f.is_valid():
                all_forms_valid = False

            if len(f.errors) or len(f.non_field_errors()):
                # check error field are not in hidden/ignored fields
                # and gether their errors as request messages
                for field in f.errors:
                    if field in f and field in f.errors:
                        all_forms_valid = False
                        error_message = u'<b>%s</b> %s' % (f[field].label, f.errors[field])
                        messages.error(request, error_message)

                for message in f.non_field_errors():
                    messages.error(request, message)
                    all_forms_valid = False
            else:
                for field in f.fields:
                    try:
                        f.fields[field].run_validators(f[field].value())
                    except ValidationError as e:
                        error_message = u'<b>%s</b> %s' % (f[field].label, e.messages )
                        messages.error(request, error_message)
                        all_forms_valid = False
                        f.errors[field] = e.messages[0]


        return all_forms_valid



    def pre_process(self, request, input_data, **kwargs):
        """
        Hook before processing the request
        Best place to make user/objects rights management
        """
        from django.db import transaction

        with transaction.atomic():
            #return super(BaseView, self).pre_process(request, input_data, **kwargs)
            # TODO
            action = kwargs.get('action', self.default_action)
            if action is None or not action:
                action = ActionView.default_action
                kwargs['action'] = action

            """
            elif not action in self.get_actions():
                logger.debug('Unknown action '+action)
                raise Http404

            if not self.__getattribute__('process_'+action):
                # this should not happen
                # log the event
                logger.error('Unknown process action code called')
                raise Http404
            """

            # get user profile object
            user_profile = self.get_user_profile(request, **kwargs)
            template_args = self.get_context_dict(request, user_profile, input_data, **kwargs)
            response = self.process(request, user_profile, input_data, template_args, **kwargs)
            return self.deliver(request, response, **kwargs)

    def process(self, request, user_profile, input_data, template_args, **kwargs):
        """
        Processes the request
        At this point, the template args context is initialized
        and the processing of the selected action is triggered
        It returns a response object
        that should come from the view render method
        but any response returned by the action is accepted
        """

        action = kwargs.get('action', None)

        if not action in self.get_actions():
            logger.error('Unknown action to process')
            raise Http404

        if action in self.get_actions() and self.__getattribute__('process_'+action):
            response = self.__getattribute__('process_'+action)(request,
                                                                user_profile,
                                                                input_data,
                                                                template_args,
                                                                **kwargs)
            return response

        else:


            result_payload = input_data
            result_message = ugettext(u'Action Not implemented:'+action)
            result_status = 'error'
            return self.render(request, result_payload, result_message,
                               result_status, **kwargs)

    def process_view(self, request, user_profile, input_data, template_args,
                     **kwargs):
        """
        Returns the view action processed data
        """
        return self.render(request, template_args, **kwargs)


    def render(self, request, template_args, **kwargs):
        """
        Render template depending on the request
        """
        #action_template = 'ilot/actions/'+self.view_name+'/'+action+kwargs['ext']
        #action = kwargs.get('action', ActionView.default_action)
        #action_template = 'actions/'+self.view_name+'/'+action+kwargs['ext']

        return render_to_response(kwargs.get('templates', self.action_templates.get(kwargs['action'], self.view_template)),
                                  template_args,
                                  context_instance=RequestContext(request),)


    def get_reversed_action(self, view_name, action, kwargs):
        """
        from a view class and action,
        reverses the action url concidering url parameters in kwargs
        kwargs['reverse_keys'] = ['key',]
        kwargs[key] = value
        does not work pretty well actually ...
        """
        reverse_kwargs = {}
        for key in kwargs.get('reverse_keys'):
            reverse_kwargs[key] = kwargs[key]

        # override action
        reverse_kwargs['action'] = action

        address = reverse(kwargs['view_name'], args=kwargs['args'], kwargs=reverse_kwargs)
        return address

    def deliver(self, request, response, **kwargs):
        """
        This final step provides the ability to lastly manage the response
        It's mainly usefull to attach tracking cookies
        """
        return response
