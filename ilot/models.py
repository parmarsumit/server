from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist

from django.db.models.fields import CharField, BooleanField, EmailField, IntegerField, TextField
from django.db.models.fields.related import ForeignKey, OneToOneField

from ilot.core.manager import AppManager

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ilot.core.models import AuditedModel, Item, DataPath
from django.utils.translation import get_language
from django.db.models import Q, F
import hashlib
from django.db.models.signals import post_save, pre_migrate
from django.dispatch import receiver

from ilot.core.models import request_switch, Moderation
from django.core.exceptions import PermissionDenied
import os

from ilot.core.models import get_locale_as_organization
from ilot.webhooks.models import Webhook
from ilot.core.parsers.api_json import load_json

try:
    from functools import reduce
except:
    pass
import operator


class Organization(AuditedModel):
    name = CharField(max_length=128, unique=True, null=True, blank=True)
    enabled = BooleanField(default=True)

    behavior = ForeignKey('rules.Action', null=True, blank=True, on_delete=models.PROTECT)
    notification = ForeignKey('grammar.Notification', null=True, blank=True, on_delete=models.PROTECT)
    webhook = ForeignKey('webhooks.Webhook', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.name)

    def get_types(self):
        from ilot.rules.models import Type
        return Type.objects.all()

    def get_actions(self):
        from ilot.rules.models import Action
        return Action.objects.all()

    def get_new_iteration(self):
        last_release = self.get_last_release()
        return Release(name=last_release.name, organization=self, iteration=last_release.iteration+1)

    def get_last_release(self):
        try:
            last_release = Release.objects.filter(organization=self).order_by('-iteration')[0]
        except IndexError:
            last_release = Release(name='initial', organization=self)
            last_release.save()
        return last_release

    def get_changes(self):
        """
        Returns changes in the app and Ui since last release
        """
        try:
            last_release = self.get_last_release()
        except IndexError:
            last_release = Release(name='initial', organization=self)
            last_release.save()

        print('since', last_release.name, last_release.created_date)

        return self.get_all_objects(since=last_release.created_date)

    def get_all_objects(self, since=None):

        model_results = []

        from ilot.models import Interface, Organization, Release, Package
        from ilot.rules.models import Action, Attribute, Condition, Property, Requirement, Rule, Status, Trigger, Type
        from ilot.grammar.models import Message, Notification, Panel
        from ilot.webhooks.models import Webhook

        for Model in (Interface, Organization, Release, Package,
                      Action, Attribute, Condition, Property, Requirement, Rule, Status, Trigger, Type,
                      Message, Notification, Panel,
                      Webhook):
            if since:
                nodes = Model.objects.filter( Q(modified_date__gt=since)|Q(created_date__gt=since)).order_by('modified_date', 'created_date')
            else:
                nodes = Model.objects.all().order_by('ref_time')

            for node in nodes:
                model_results.append(node)

        print('TOTAL', len(model_results))

        return model_results


class Interface(AuditedModel):
    cname = CharField(max_length=128, unique=True, null=True, blank=True)
    application = ForeignKey(Organization,
                             related_name='interfaces',
                             null=True, blank=True,
                             db_constraint=False, on_delete=models.PROTECT)
    action = ForeignKey('rules.Action',
                        null=True, blank=True,
                        db_constraint=False, on_delete=models.PROTECT)
    content = TextField(default='{% extends "index.html" %}')
    data = TextField(default="{}")

    repository = CharField(max_length=512, null=True, blank=True)

    def get_absolute_path(self):
        # evaluate path from repository field
        return settings.SERVER_ROOT+'/'+self.id

    def __str__(self):
        return str(self.cname)

    def get_data(self):
        return load_json(self.data)

    def get_settings(self):
        # get current running app settings
        settings = {}

        settings['mailjet_api_key'] = os.environ.get('MAILJET_API_KEY', settings.MAILJET_API_KEY)
        settings['mailjet_api_secret'] = os.environ.get('MAILJET_API_SECRET', settings.MAILJET_API_SECRET)
        settings['mailjet_from_email'] = os.environ.get('MAILJET_FROM_EMAIL', settings.MAILJET_FROM_EMAIL)
        
        return settings

    def get_applications(self):
        return Organization.objects.all()

    def get_ip(self):
        return None
        """
        Resolve IP from cname
        """
        try:
            import socket
            return socket.gethostbyname(self.cname)
        except:
            return None

    def is_local(self):
        return False
        """
        https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        """
        import socket
        local_ip = socket.gethostbyname_ex(request_switch.host.split(':')[0])[2][0]

        #print(local_ip, self.get_ip())

        if local_ip == self.get_ip():
            return True
        else:
            return False


class Release(AuditedModel):

    name = CharField(max_length=128)

    organization = ForeignKey(Organization, null=True, blank=True,
                              related_name='releases',
                              db_constraint=False, on_delete=models.PROTECT)

    iteration = IntegerField()

    decription = TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        unique_together = ['organization', 'iteration']

    def save(self):
        self.iteration = Release.objects.filter(organization=self.organization).count()
        super(Release, self).save()



class Package(AuditedModel):
    name = CharField(max_length=128)
    organization = ForeignKey(Organization,
                              null=True, blank=True, related_name='packages',
                              db_constraint=False, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.name)

    def get_actions_names(self):
        return self.actions.values_list('name', flat=True)

    def get_actions_ids(self):
        return self.actions.values_list('name', flat=True)

    def get_types_names(self):
        return self.types.values_list('name', flat=True)

    def get_types_ids(self):
        return self.types.values_list('name', flat=True)

    # TODO:
    # Manage dependencies graph


def has_perm(action, organization, akey, item, ext=None, method=None):

    # check for top level acces tokens for profile
    #if organization and profile and item:
    access_links = Authorization.objects.filter(organization=organization,
                                                akey=akey,
                                                origin=item.id,
                                                action=action,
                                                enabled=False)
    if access_links.count():
        return True
    else:
        return has_rule(action, organization, akey, item)

def has_rule(action, organization, akey, item):

    from ilot.rules.models import Rule

    if True == False:

        if action in item.get_action_names():
            return True
        else:
            return False

    # has perm
    permissions = Rule.objects.filter(action__name=action, enabled=True)
    #, locale=organization)
    permissions = permissions.filter(type__in=item.get_infered_types() )
    permissions = permissions.filter(actor__in=item.get_my_infered_types() )

    if permissions.filter(is_allowed=False).count():
        return False
    elif permissions.count():
        return True
    else:
        return False


def filter_with_perm(action, organization, akey, items):
    """
    Filter an item list by action permissions
    Returns an item query set filtered using the permissions

    The method is dirty actually as it runs a test against all provided items
    It should be rewritten to be filtered as a query
    """
    return filter_with_rules(action, organization, akey, items)

def filter_with_rules(action, organization, akey, items):
    # TODO
    # find better solution to filter by possible action
    ids = []
    for item in items:
        if has_rule(action, organization, akey, item):
            ids.append(item.id)
    return items.model.objects.filter(id__in=ids)



class Authorization(AuditedModel):
    organization = ForeignKey(Organization, blank=True, null=True, related_name='tokens', on_delete=models.PROTECT)
    #token = CharField(max_length=36, unique=True, default=AppManager.get_new_uuid)
    #email = EmailField(blank=True, null=True)
    akey = CharField(max_length=36, blank=True, null=True)
    origin = CharField(max_length=36, blank=True, null=True)
    action = CharField(max_length=36, blank=True, null=True)

    # a verification token
    # originally a tx for receipt lookup
    # token = CharField(max_length=128, blank=True, null=True)

    payload = TextField(default='{}')

    enabled = BooleanField(default=True)

    def get_url(self):
        return 'https://'+request_switch.host+'/'+self.id+'/'

    def get_data(self):
        return load_json(self.payload)
