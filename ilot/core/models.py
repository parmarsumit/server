'''
Created on 15 janv. 2013

@author: rux
'''
from collections import OrderedDict
from datetime import datetime
import hashlib
import logging
import math
import operator
import os
from time import mktime
import time
import traceback
import unicodedata
import uuid
import pytz

from django.conf import settings
from django.core.cache import cache as object_cache
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from django.core.files.base import File
from django.db import models
from django.db.models.fields import TextField
from django.db.models.manager import Manager
from django.db.models.query import QuerySet, F
from django.db.models.query_utils import Q
from django.forms.models import model_to_dict
from django.utils import translation
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from django.utils.translation import get_language as get_locale

from ilot.core.manager import AppManager

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from ilot.core.manager import AppManager
from ilot.core.parsers.api_json import load_json, dump_json
from ilot.core.utils.compatibility import unicode3

from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType



try:
    from urllib.parse import unquote
except:
    from urllib import unquote

try:
    from functools import reduce
except:
    pass
import operator

from django.conf import settings

logger = logging.getLogger(__name__)


def get_default_locale():
    return get_locale_as_organization()

def get_locale_as_organization():
    return request_switch.interface.id


import threading

global request_lock
request_lock = threading.RLock()

global request_switch
request_switch = threading.local()

if not hasattr( request_switch, 'host' ):
    request_switch.host = ''

if not hasattr( request_switch, 'url' ):
    request_switch.url = ''

if not hasattr( request_switch, 'organization' ):
    request_switch.organization = None

if not hasattr( request_switch, 'akey' ):
    request_switch.akey = None


class ModelDiffMixin(object):
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    def has_changed(self, field_name=None):
        if field_name:
            if field_name in self.changed_fields:
                return True
        else:
            return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    def get_as_dict(self):
        return self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])



class AuditedModel(ModelDiffMixin, models.Model):
    '''
    An abstract model to add creation and modification values
    '''
    id = models.CharField(primary_key=True, default=AppManager.get_new_uuid, editable=False, max_length=128)

    #
    version = models.IntegerField(default=0, editable=False)

    #
    ref_time = models.BigIntegerField(editable=False, default=AppManager.get_ref_time)

    #
    created_date = models.DateTimeField(_('created on'), editable=False, default=AppManager.get_valid_time)
    modified_date = models.DateTimeField(_('modified on'), editable=False, null=True, blank=True)

    class Meta:
        abstract = True

    @staticmethod
    def get_ref_time():
        # ref_time has to be set using UTC
        return time.time()*100000

    @staticmethod
    def get_valid_time():
        return now()

    def get_uuid_hex(self):
        import uuid
        uuidObject = uuid.UUID(self.id)
        return uuidObject.hex

    def get_model_name(self):
        return self.__class__.__name__

    def get_package_name(self):
        try:
            return self.package.name
        except:
            try:
                return self.action.package.name
            except:
                try:
                    return self.type.package.name
                except:
                    return '--------'

        return self._meta.app_label

    def full_clean(self, exclude=None, validate_unique=True):
        if not self.ref_time:
            self.ref_time = AuditedModel.get_ref_time()

        super(AuditedModel, self).full_clean(exclude=exclude, validate_unique=validate_unique)

    def ref_date(self):
        return pytz.utc.localize(datetime.fromtimestamp(self.ref_time/100000))

    def get_relators(self):
        """
        # TODO
        returns all the items relating to this item
        this method is from old version
        """
        targets = []

        for att in self.get_attributes():
            #print(att)
            try:
                item = Item.objects.get_at_id(att['value'])
                targets.append(item.id)
            except:
                continue

        #rel_ids = Moderation.objects.filter(Q(Q(id__in=targets)|Q(related__parent_id=self.id)|Q(value=self.id)|Q(data__contains='"'+self.id+'"'))).order_by('-ref_time', 'type')
        return Item.objects.filter(Q(Q(id__in=targets)|Q(parent_id=self.id)|Q(target=self.id)|Q(data__contains='"'+self.id+'"'))).order_by('-ref_time', 'type')


    def save(self, *args, **kwargs):

        #
        if 'using' in kwargs:
            return super(AuditedModel, self).save(*args, **kwargs)

        self.full_clean()

        # Some child implementations (like VersionedModel) want to persist the created_date
        # of the oldest ancestor.  This check thus allows that.
        now_dtz = now()

        if not self.created_date:
            self.created_date = now_dtz
        if not self.ref_time:
            self.ref_time = AuditedModel.get_ref_time()

        self.modified_date = now_dtz
        self.version += 1
        super(AuditedModel, self).save(*args, **kwargs)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class GantChartMixin(object):

    def get_start_timestamp(self):
        if self.start:
            start = self.start
        else:
            start = self.created_date

        from django.utils.dateformat import format
        return int(format(start, 'U'))

    def get_now_timestamp(self):
        from django.utils.dateformat import format
        return int(format(datetime.now(), 'U'))

    def get_end_timestamp(self):
        if self.end:
            end = self.end
        else:
            end = datetime.now()
            end.replace(year=end.year+1)
        from django.utils.dateformat import format
        return int(format(end, 'U'))


    def get_start_ratio(self):
        """
        return start ratio from now within year
        """
        year_seconds = 365*24*60*60
        this_duration = self.get_start_timestamp() - self.get_now_timestamp()
        return (this_duration/year_seconds)*100

    def get_duration_ratio(self):
        """
        return duration ratio from now within year from now as base
        """
        year_seconds = 365*24*60*60
        this_duration = self.get_end_timestamp() - self.get_start_timestamp()
        return (this_duration/year_seconds)*100

    def get_end_ratio(self):
        """
        return end ratio from now with year from now as base
        """
        year_seconds = 365*24*60*60
        this_duration = self.get_now_timestamp() - self.get_end_timestamp()
        return (this_duration/year_seconds)*100

class GantChartModel(GantChartMixin):

    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class ObjectTree(dict):
    """
    TODO
    Review the original switch and purge invalidate

    Object instance cache tree
    """
    def __get_db__(self):
        if request_switch.organization:
            return request_switch.organization.id
        else:
            return 'default'

    def __get_space__(self, space_name=None):

        if not space_name:
            space_name = self.__get_db__()

        if not space_name in self.__dict__:
            self.__dict__[space_name] = {}

        return self.__dict__[space_name]

    def __init__(self):
        self.__get_space__()
        return super(ObjectTree, self).__init__()

    def __getitem__(self, key):
        return self.__get_space__()[key]

    def __setitem__(self, key, value):
        #print('CACHING KEY', key)
        self.__get_space__()[key] = value

    def __delete__(self, key):
        del self.__get_space__()[key]

    def __contains__(self, key):
        # check if key in the cache
        if key in self.__get_space__():
            return True
        else:
            return False

    def remove(self, key):
        if key in self.__get_space__():
            del self.__get_space__()[key]

    def purge(self):
        """
        Purge the tree from invalid instances
        """
        if not 'last_ref_time' in Item.objects.tree_times:
            print('Intit CACHING FOR '+self.__get_db__())
            Item.objects.tree_times['last_ref_time'] = AuditedModel.get_ref_time()
            Item.objects.tree_times['last_mod_time'] = AuditedModel.get_valid_time()

        #print('CALLING PURGE for '+self.__get_db__(), Item.objects.tree_times['last_ref_time'])

        # before this point we have to check for cached items invalidation
        new_items = list(set(Moderation.objects.filter( Q(Q(ref_time__gt=Item.objects.tree_times['last_ref_time'])|Q(modified_date__gt=Item.objects.tree_times['last_mod_time'])) ).values_list('related_id', flat=True).distinct().order_by('related_id')[:250]))
        if len(new_items) < 1000:
            if new_items:
                new_uids = list(set(new_items))
                #print(Item.objects.tree_times['last_ref_time'], 'Purging ', new_items)
                for uid in new_uids:
                    if uid in Item.objects.tree_map:
                        Item.objects.remove_tree_cache(object_tree_cache[uid])

            # we check for item parents too
            parent_items = Item.objects.filter(id__in=new_items).values_list('parent_id', flat=True)
            if parent_items:
                parent_ids = list(set())
                print(Item.objects.tree_times['last_ref_time'], 'Purged ', parent_ids)
                for uid in parent_ids:
                    if uid in object_tree_cache:
                        del object_tree_cache[uid]['children_qs']
                        del object_tree_cache[uid]['children_count']
                    if uid in Item.objects.tree_map:
                        Item.objects.remove_tree_cache(object_tree_cache[uid])

            Item.objects.tree_times['last_ref_time'] = AuditedModel.get_ref_time()
            Item.objects.tree_times['last_mod_time'] = AuditedModel.get_valid_time()
        else:
            print ('TOO MANY OBJECTS TO PURGE FROM CACHE ', len(new_items))
        #print('PURGED')


global object_tree_cache
object_tree_cache = ObjectTree()


class DataPath(AuditedModel):
    """
    Base Model
    """
    __inited__ = False
    _data = None
    _saved = False
    #
    akey = models.CharField(max_length=128)
    #
    action = models.CharField(max_length=36, null=True, blank=True)
    # rename to ns
    locale = models.CharField(max_length=36, null=False, blank=False)
    #
    geohash = models.CharField(max_length=12, blank=True, null=True)
    #
    data = TextField(default='{}', blank=True, null=True)
    #
    context = models.CharField(max_length=36, null=True, default='')

    #
    visible = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return self.id

    def __init__(self, *args, **kwargs):
        super(DataPath, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):

        if 'using' in kwargs:
            return super(DataPath, self).save(*args, **kwargs)

        if not self.locale:
            self.locale = get_locale_as_organization()

        #self.data = dump_json(self.get_data())
        super(DataPath, self).save(*args, **kwargs)

    def get_url(self):
        if not self.id in Item.objects.tree_mods:
            return Moderation.objects.get(id=self.id).get_url()
        else:
            return Item.objects.tree_mods[self.id]

    def get_context(self):
        return Item.objects.get_at_id(self.context)

    def get_locale(self):
        return Item.objects.get_at_id(self.locale)

    def get_index(self):
        """
        TODO
        returns the item index in the children list
        """
        return self.order

    def get_as_dict(self):
        model_data = model_to_dict(self)
        # exclude model internal django relations
        for k in ('related',
                  'parent',
                  'origin',
                  'datapath_ptr',
                  'moderation_ptr',
                  'translation_ptr',
                  'item_ptr'):
            if k in model_data:
                del model_data[k]

        return model_data

    def get_actor(self):
        return Item.objects.get_at_id(self.akey)

    def get_item(self):
        """
        DEPRECATED
        """
        return self

    def get_profile(self):
        """
        DEPRECATED
        """
        return self.get_actor()


    def get_data(self, refresh=False):
        """
        return the data block as dict
        """
        if not refresh and self.id in Item.objects.tree_id_data:
            return Item.objects.tree_id_data[self.id]

        if not refresh and self._data:
            return self._data

        data_dict = {}
        from ilot.data.models import DataBlock
        data_blocks = DataBlock.objects.filter(origin=self.id).order_by('-ref_time')
        if len(data_blocks):
            values = data_blocks.values_list('name', 'value')
            for value in values:
                data_dict[value[0]] = value[1]
            self._data = data_dict
        else:
            self._data = {}

        if self._state.db:
            Item.objects.tree_id_data[self.id] = self._data

        return self._data


class Moderation(DataPath):
    """
    Respresents a user comment or item changes
    """
    # action status
    status = models.CharField(max_length=65)

    # order in list of children
    order = models.IntegerField(default=0)

    # moderation origin
    origin = models.ForeignKey("Moderation", related_name='followings', blank=True, null=True, editable=False, db_constraint=False, on_delete=models.CASCADE)

    # item related
    related = models.ForeignKey("Item", related_name="events", editable=False, db_constraint=False, on_delete=models.CASCADE)

    # item target
    target = models.CharField(max_length=36)

    # type infered
    type = models.CharField(max_length=36, blank=True, null=False)

    #
    def __unicode__(self):
        return self.id+' ('+self.action+'/'+self.status+')'

    def __init__(self, *args, **kwargs):
        super(Moderation, self).__init__(*args, **kwargs)
        if self.status:
            self._update_statuses()

    def _update_statuses(self):

        if not self.status:
            print('NO STATUS')
            raise

        if not self.related_id:
            raise

        if self.related_id != self.id:
            Item.objects.tree_id_statuses[self.id] = [self.status]
        else:
            # query item statuses if not already cached
            if not self.related_id in Item.objects.tree_id_statuses:
                statuses = list(Moderation.objects.filter(related_id=self.related_id).values_list('status', flat=True).distinct())
                Item.objects.tree_id_statuses[self.related_id] = statuses

        if self.related_id in Item.objects.tree_id_statuses:
            if not self.status in Item.objects.tree_id_statuses[self.related_id]:
                Item.objects.tree_id_statuses[self.related_id].append(self.status)

        if self.id in Item.objects.tree_actor_statuses:
            if self.akey in Item.objects.tree_actor_statuses[self.id]:
                if not self.status in Item.objects.tree_actor_statuses[self.id][self.akey]:
                    Item.objects.tree_actor_statuses[self.id][self.akey].append(self.status)

        if self.id in Item.objects.tree_target_statuses:
            if self.target in Item.objects.tree_target_statuses[self.id]:
                if not self.status in Item.objects.tree_target_statuses[self.id][self.target]:
                    Item.objects.tree_target_statuses[self.id][self.target].append(self.status)

            #print('UPDATED '+self.related_id+' STATUSES', Item.objects.tree_id_statuses[self.related_id])


    def __getattr__(self, key):

        # override access to related
        if key in ('related',):
            try:
                return Item.objects.get_at_id(self.related_id)
            except ObjectDoesNotExist:
                return super(Moderation, self).__getattribute__(key)

        if key in ('origin',):

            if self.origin_id == self.id:
                return self

            if not self.origin_id in Item.objects.tree_mods:
                try:
                    Item.objects.tree_mods[self.origin_id] = Moderation.objects.get(id=self.origin_id)
                except ObjectDoesNotExist:
                    return super(Moderation, self).__getattribute__(key)
            return Item.objects.tree_mods[self.origin_id]

        elif key in super(Moderation, self).__dict__:
            return super(Moderation, self).__dict__[key]

        return super(Moderation, self).__getattribute__(key)


    def __getattribute__(self, attr):

        # avoid looping on attribute
        if attr in ('_data', 'get_data', '__cache__', '__inited__', '__dict__'):
            return super(Moderation, self).__getattribute__(attr)

        # override access to related
        elif attr in ('related',):
            try:
                return Item.objects.get_at_id(self.related_id)
            except ObjectDoesNotExist:
                return super(Moderation, self).__getattribute__(key)

        elif attr in ('origin',):
            if not self.origin_id in Item.objects.tree_mods:
                Item.objects.tree_mods[self.origin_id] = Moderation.objects.get(id=self.origin_id)
                #super(Moderation, self).__getattribute__(key)
            return Item.objects.tree_mods[self.origin_id]

        elif attr.startswith('query_'):
            return self.__query(attr)

        elif attr.startswith('can_'):
            return self.__can(attr)

        elif attr.startswith('is_'):
            return self.__is(attr)

        elif attr.startswith('iam_'):
            return self.__iam(attr)

        elif attr.startswith('get_image'):
            return self.__image(attr)

        elif attr in super(Moderation, self).__dict__:
            return super(Moderation, self).__dict__[attr]

        elif super(Moderation, self)._data and attr in super(Moderation, self)._data:
            return super(Moderation, self)._data[attr]

        return super(Moderation, self).__getattribute__(attr)


    def do_query(self, attr):
        query = ''
        if isinstance(attr, dict):
            for key in attr:
                query += '_'+key
                if attr[key]:
                    query += '_'+str(attr[key]).replace(' ','_')
        else:
            query = attr

        return self.__query(str(query))

    __cachedqueries__ = {}

    def __query(self, attr):
        """
        ILOT query parser
        """
        try:
            AppManager.cache_lists()

            if settings.CACHE_CORE_QUERIES:
                if self.id in self.__cachedqueries__:
                    if attr in self.__cachedqueries__[self.id]:
                        return self.__cachedqueries__[self.id][attr]

            #if settings.DEBUG:
            #    print('QUERY:', '/tools/query.html?id='+self.id+'&query='+attr)

            #
            statuses = AppManager.statuses_list #['indexed', 'drafted', 'initialized', 'rewarded', 'budgeted', 'assigned', 'calling']
            actions = AppManager.actions_list #['index', 'view', ]
            ntypes = AppManager.types_list #['Project', 'Initiator', 'Contribution', 'RewardedContribution', 'Initiative']
            attributes = AppManager.attributes_list #['value', 'amount', ]

            methods = ['total', 'count', 'list']

            #
            perm_action = None
            params = attr.split('_')

            attr = None
            method = None

            if 'query' in params:
                params.remove('query')

            type_accu = []

            #result = self.__class__.objects.filter(visible=True)
            relator = self.related

            result = Moderation.objects.filter(visible=True)
            typed_items = None
            events = False

            for param in params:

                if param in statuses:
                    result = result.filter(status=param)

                elif param == 'my':
                    result = result.filter(target=request_switch.akey)
                    events = True

                elif param == 'acting':
                    result = result.filter(akey=self.related_id)
                    events = True

                elif param == 'his':
                    result = result.filter(target=self.related_id)
                    events = True

                elif param == 'is':
                    result = result.filter(id=self.id)

                elif param == 'this':
                    result = result.filter(related_id=self.related_id)

                elif param == 'following':
                    result = result.filter(origin_id=self.id)

                elif param == 'with':
                    result = Moderation.objects.filter(related_id__in=result.values_list('related_id', flat=True).distinct())

                elif param == 'children':
                    result = result.filter(related__parent_id=relator.related_id)

                elif param == 'descendants':
                    # at root
                    if relator.parent_id == None:
                        result = result.filter(related__context=relator.id)
                    # at LX
                    else:
                        # childrens of L1 > L2
                        items = Item.objects.filter(related__parent_id=relator.related_id)

                        # childrens of L2 > L3
                        items = Item.objects.filter(Q(id__in=items)
                                                    |Q(parent_id__in=items))
                        # childrens of L3 > L4
                        items = Item.objects.filter(Q(id__in=items)
                                                    |Q(parent_id__in=items))
                        # childrens of L4 > L5
                        items = Item.objects.filter(Q(id__in=items)
                                                    |Q(parent_id__in=items))


                        result = result.filter(related_id__in=items.values_list('id', flat=True))

                elif param == 'incontext':
                    #if not typed_items:
                    result = result.filter(context=request_switch.context)
                    relator = Item.objects.get_at_id(request_switch.context)
                        #result = result.filter(context=self.context)

                elif param == 'context':
                    #if not typed_items:
                    result = result.filter(context=self.context)
                    relator = Item.objects.get_at_id(self.context)

                elif param in attributes:
                    #result = result.filter(status=param)
                    attr = param

                elif param in methods:
                    method = param

                elif param in ntypes:

                    # get the typed item related to the event
                    from ilot.rules.models import Type
                    ntype = Type.objects.get(name=param)


                    if ntype.reference == 'target':
                        events = True
                        if not 'targets' in params:
                            params.append('targets')

                    elif ntype.reference == 'actor':
                        events = True
                        if not 'actors' in params:
                            params.append('actors')

                    elif ntype.reference == 'event':
                        events = True

                    typed_items = self.get_typed(ntype, events=events)

                    #if not typed_items.count():
                        #print('No typed ', ntype, relator.context)
                    #    result = result.none()
                    #else:

                    result = result.filter(id__in=typed_items.values_list('id', flat=True))
                        #print(ntype, typed_items)

                elif param in actions:
                    #print ('ACTION', param)
                    perm_action = param

                elif param == 'items':
                    result = Moderation.objects.filter(id__in=result.values_list('related_id', flat=True).distinct())

                elif param == 'contexts':
                    result = Moderation.objects.filter(id__in=result.values_list('context', flat=True).distinct())

                elif param in ['all', 'feed', 'following', 'incontext', 'context', 'items', 'targets', 'actors', 'contexts', 'notifications', 'todos', 'latest', 'query']:
                    pass
                else:
                    if param:
                        result = result.none()
                        print('--- CANNOT QUERY PARAM ', param)


            if 'notifications' in params or 'todos' in params:

                only_todo = False
                if 'todos' in params:
                    only_todo = True

                from ilot.meta.models import ActorInferedType, ActorNotification
                all_notifs_scopes = []

                #notifications = ActorInferedType.objects.filter(context__in=result, actor_id=request_switch.akey)
                notifications = ActorNotification.objects.filter(context__actor_id=request_switch.akey)

                # exclude discarded notifications
                discarding_rules = notifications.filter(rule__discards__isnull=False)
                discarded_rules = discarding_rules.values_list('rule__discards_id', flat=True)

                notifications = notifications.exclude(rule__in=discarded_rules,
                                                      event_id__in=discarding_rules.values_list('event__origin_id', flat=True))

                #
                notifications = notifications.exclude(rule__silent=True)

                if only_todo:
                    notifications = notifications.filter(rule__todo=only_todo)

                result = result.filter(id__in=notifications.values_list('event_id', flat=True).distinct())

            # filter with status properties
            from ilot.rules.models import Status

            if 'feed' in params:
                visible_statuses = Status.objects.filter(silent=False).values_list('name', flat=True)
                result = result.filter(status__in=visible_statuses)


            shared_statuses = Status.objects.filter(shared=True).values_list('name', flat=True)
            result = result.filter( Q(locale=request_switch.interface.id) | Q(status__in=shared_statuses) )
            result = result.order_by('-ref_time')

            if 'items' in params:
                result = Item.objects.filter(id__in=result.values_list('related_id', flat=True).distinct())

            elif 'targets' in params:
                result = Item.objects.filter(id__in=result.values_list('target', flat=True).distinct())

            elif 'actors' in params:
                result = Item.objects.filter(id__in=result.values_list('akey', flat=True).distinct())

            elif 'contexts' in params:
                result = Item.objects.filter(id__in=result.values_list('context', flat=True).distinct())

            if perm_action:
                from ilot.models import filter_with_perm
                result = filter_with_perm(perm_action, request_switch.organization, request_switch.akey, result)


            #
            if method == 'list':
                value = ''
            else:
                value = 0

            if method:
                #print('METHOD', method, attr)

                if method == 'timeframed' or method == 'bymonth':
                    # sample the value over the request timeframe
                    start = request_switch.start
                    end = request_switch.end

                elif method == 'count':
                    value  = result.count()

                elif method == 'total':
                    for item in result:
                        value += float(item.get_data().get(attr, 0))

                elif method == 'list':
                    count = result.count()
                    i = 0
                    for item in result:
                        v = item.get_data().get(attr)
                        value += str(v)
                        i += 1
                        if i < count:
                            value += ','


                final_query_result = value

            else:
                if 'latest' in params:
                    try:
                        final_query_result = result[0]
                    except IndexError:
                        return None
                else:
                    final_query_result = result

            if settings.CACHE_CORE_QUERIES:
                if not self.id in self.__cachedqueries__:
                    self.__cachedqueries__[self.id] = {}
                self.__cachedqueries__[self.id][attr] = final_query_result

            return final_query_result
        except:
            traceback.print_exc()

    def __can(self, attr):
        from ilot.models import has_perm
        return has_perm(attr[4:], request_switch.organization, request_switch.akey, self)

    def __is(self, attr):
        from ilot.rules.models import Type
        try:
            ntype = Type.objects.get(name=attr[3:])
        except Type.DoesNotExist:
            print('Unknwon type ', attr[3:])
            return False

        if ntype.reference == 'actor':
            return attr[3:] in list(self.get_actor_infered_types(self.akey).values_list('name', flat=True))
        elif ntype.reference == 'target':
            return attr[3:] in list(self.get_actor_infered_types(self.target).values_list('name', flat=True))
        else:
            return attr[3:] in list(self.get_infered_types().values_list('name', flat=True))

    def __iam(self, attr):
        return attr[4:] in list(self.get_my_infered_types().values_list('name', flat=True))

    def get_action(self):
        from ilot.rules.models import Action
        try:
            return Action.objects.get(name=self.action)
        except:
            print('CANNOT FIND ACTION ', self.action)
            return None

    def get_display(self):
        """
        Get a human readable text
        """
        types = self.get_infered_types()

        display_key = None
        for type in types:
            if type.display_field:
                display_key = type.display_field.name
                if display_key in self.get_data():
                    break

        if display_key:
            display_text = self.get_data().get(display_key)
        else:
            if 'username' in self.get_data():display_key = 'username'
            elif 'title' in self.get_data():display_key = 'title'

        display_text = self.get_data().get(display_key)

        if not display_text:
            # TODO
            # search for word or title field
            pass
            return self.get_data()
        else:
            return display_text


    __images__ = {}

    def __image(self, attr_line):

        #


        # get maybe an id saved
        image_id = None
        if attr_line != 'get_image':
            attr = attr_line[len('get_image_'):]
            image_id = self.get_data().get(attr)
        else:
            attr = 'image'

        from ilot.medias.models import Media

        if not self.id in Item.objects.tree_images:
            Item.objects.tree_images[self.id] = {}

        if attr in Item.objects.tree_images[self.id] \
            and image_id in Item.objects.tree_images[self.id]:
            return Item.objects.tree_images[self.id][attr]

        try:
            if image_id:
                media = Media.objects.get(id=image_id)
            else:
                media = Media.objects.filter(item=self.id).order_by('-ref_time')[0]

            image = media.image
            image.avatar = media.avatar
            image.thumbnail = media.thumbnail
            Item.objects.tree_images[self.id][attr] = image
            return image

        except IndexError:
            types = self.get_infered_types()
            if len(types) > 0:
                for type in types:
                    if type.image:
                        type.image.avatar = type.avatar
                        type.image.thumbnail = type.thumbnail
                        Item.objects.tree_images[self.id][attr] = type.image
                        return type.image

        # generate identicon
        print('GENERATING identicon')

        import pydenticon
        generator = pydenticon.Generator(5, 5)

        identicon_path = settings.MEDIA_ROOT+'/CACHE/'+self.id+'.png'


        if not os.path.exists(identicon_path):
            identicon_png = generator.generate(self.id, 256, 256, output_format="png")

            f = open(identicon_path, "wb")
            f.write(identicon_png)
            f.close()

        from django.db.models.fields.files import FieldFile

        media = Media()

        image = FieldFile(self, media.image, 'CACHE/'+self.id+'.png')
        image.avatar = FieldFile(self, media.avatar, 'CACHE/'+self.id+'.png')
        image.thumbnail = FieldFile(self, media.thumbnail, 'CACHE/'+self.id+'.png')

        Item.objects.tree_images[self.id][attr] = image
        print(image.path)

        return image

    def get_my_notifications(self):

        from ilot.meta.models import ActorNotification
        anotifs = ActorNotification.objects.filter(event_id=self.id, context__actor_id=request_switch.akey)

        from ilot.grammar.models import Notification
        return Notification.objects.filter(id__in=anotifs.values_list('rule_id', flat=True))


    def get_stream(self, ascending=None, include_self=True):
        """

        """
        # TODO
        # maintian cache
        return Moderation.objects.filter(related=self.related, ref_time__gt=self.ref_time)

    def get_tree(self):
        """
        Return a tree of the past and futur of the event
        """
        # TODO
        # maintian cache
        return Moderation.objects.filter(related_id=self.id)

    def get_history(self, ascending=None, include_self=True):
        """
        Returns the ancestors of the event
        """
        if self.origin_id == self.id:
            if include_self == True:
                return [self]
            else:
                return []
        else:
            ac = 0
            if include_self:
                ancestors = [self]
            else:
                ancestors = []
            a = self
            while a.origin and a.origin_id and not a.origin in ancestors and ac < 10:
                ancestors.append(a.origin)
                a = a.origin
                ac += 1
                if not a.origin:
                #    ancestors.append(a)
                    break
            #return ancestors
            return list(reversed(ancestors))

    def get_interface(self):
        try:
            from ilot.rules.models import Status
            Status.objects.get(name=self.status, shared=True)
            return request_switch.interface
        except Status.DoesNotExist:
            try:
                from ilot.models import Interface
                return Interface.objects.get(id=self.locale)
            except ObjectDoesNotExist:
                return request_switch.interface

    def get_url(self):
        interface = self.get_interface()

        if settings.DEBUG:
            hp = request_switch.host.split(':')
            if len(hp) > 1 and settings.DEBUG:
                return 'https://'+interface.cname+':'+hp[1]+'/'+self.id+'/'
            else:
                return 'https://'+interface.cname+'/'+self.id+'/'
        else:
            return 'https://'+interface.cname+'/'+self.id+'/'

    def get_target(self):
        return Item.objects.get_at_id(self.target)

    def get_ancestors(self, ascending=None, include_self=True):
        """
        DEPRECATED

        conflicts with Item.get_ancestors
        """
        if self.origin_id == self.id:
            if include_self == True:
                return [self]
            else:
                return []
        else:
            ac = 0
            if include_self:
                ancestors = [self]
            else:
                ancestors = []
            a = self
            while a.origin and a.origin_id and not a.origin in ancestors and ac < 10:
                ancestors.append(a.origin)
                a = a.origin
                ac += 1
                if not a.origin:
                #    ancestors.append(a)
                    break
            #return ancestors
            return list(reversed(ancestors))

    def get_type(self):
        from ilot.rules.models import Type
        try:
            return Type.objects.get(name=self.type)
        except ObjectDoesNotExist:
            return None

    def get_typed(self, ntype, events=False, scoped=False, from_event_id=None):

        # TODO
        # handle CACHE properly
        # settings.CACHE_TYPED_LISTS = False
        if not scoped and settings.CACHE_TYPED_LISTS and events and ntype.id in Item.objects.tree_context_typed:
            typed = Moderation.objects.filter(id__in=Item.objects.tree_context_typed[ntype.id])
        else:
            #
            if not ntype.type or ntype.type == ntype:
                type_base = Moderation.objects.all()
            else:
                if ntype.type.reference in ('related', 'context', 'item'):
                    type_base = Moderation.objects.filter(origin__related_id__in=self.get_typed(ntype.type))
                elif ntype.type.reference in ('event',):
                    type_base = Moderation.objects.filter(origin_id__in=self.get_typed(ntype.type))
                else:
                    type_base = Moderation.objects.all()

            #
            if scoped:
                if ntype.scope == 'event':
                    type_base = type_base.filter( Q(id=self.id)|Q(id=self.origin_id) )
                elif ntype.scope == 'item':
                    type_base = type_base.filter( Q(id=self.id)|Q(id=self.origin_id)|Q(related_id=self.related_id) )
                elif ntype.scope == 'descendants':
                    pass
                elif ntype.scope == 'children':
                    pass

            #
            typed = type_base.filter(status=ntype.status.name)

            from ilot.rules.models import Type
            if not ntype.id in Type.objects.overrides_statuses:
                overrides = Type.objects.filter(overrides=ntype, overrides__reference=ntype.reference)
                overrides_statuses = list(overrides.values_list('status__name', flat=True))
                Type.objects.overrides_statuses[ntype.id] = overrides_statuses
            else:
                overrides_statuses = Type.objects.overrides_statuses[ntype.id]

            #print('TYPED OVERRIDES', overrides_statuses, 'over', typed.count())

            for overriding_status in overrides_statuses:

                if True==False:
                    if ntype.reference == 'target':
                        exclude = Q( id__in=type_base.filter(status=overriding_status).values_list('origin_id', flat=True) )
                    elif ntype.reference == 'actor':
                        exclude = Q( id__in=type_base.filter(status=overriding_status).values_list('origin_id', flat=True) )
                    elif ntype.reference == 'related':
                        exclude = Q( id__in=type_base.filter(status=overriding_status).values_list('related_id', flat=True) )
                    elif ntype.reference == 'event':
                        exclude = Q( id__in=type_base.filter(status=overriding_status).values_list('origin_id', flat=True) )
                    elif ntype.reference == 'context':
                        exclude = Q( id__in=type_base.filter(status=overriding_status).values_list('related_id', flat=True) )

                    # exclude = Q( id__in=type_base.filter(status=overriding_status).values_list('id', flat=True) )
                    # type_base = type_base.exclude(exclude)
                    # if overrides.count():

                type_over = type_base.filter(status=overriding_status)

                if from_event_id:
                    type_over = type_over.exclude(id=from_event_id)

                exclude = Q( id__in=type_over.values_list('origin_id', flat=True) )

                #print('EXCLUDING', type_base.filter(status=overriding_status).values_list('origin_id', flat=True).distinct().count(),
                #                   overriding_status,' from ', typed.count(), ntype.status )
                #print( Moderation.objects.filter(exclude).values_list('id') )
                typed = typed.exclude(exclude)

            #print('FINALLY ', typed.count(), typed.values_list('id'))
                #print('EXLUDING mods ', type_base.filter(exclude).values_list('id'), )
                #print('EXCLUDED', overriding_status, typed.count(), type_base.filter(exclude).count() )

            typed = typed.distinct()

            if not scoped:
                Item.objects.tree_context_typed[ntype.id] = typed.distinct()

        if events:
            return Moderation.objects.filter(id__in=Item.objects.tree_context_typed[ntype.id])
        else:
            if ntype.reference == 'target':
                typed = typed.values_list('target', flat=True)
            elif ntype.reference == 'related':
                typed = typed.values_list('related_id', flat=True)
            elif ntype.reference == 'actor':
                typed = typed.values_list('akey', flat=True)
            elif ntype.reference == 'event':
                typed = typed.values_list('id', flat=True)
            elif ntype.reference == 'context':
                typed = typed.values_list('context', flat=True)
            else:
                print('NO TYPE REF')

            return typed.distinct()


    def get_actor_by_type(self, atype):

        akeys = [self.akey]
        if self.target != self.akey:
            akeys.append(self.target)

        if self.related_id == self.id:

            for event in self.related.events.filter(origin_id=self.id):
                if not event.akey in akeys:
                    akeys.append(event.akey)
                if not event.target in akeys:
                    akeys.append(event.target)

        results = []
        for akey in akeys:
             if not akey in results \
                and atype in self.get_actor_infered_types(akey):
                 results.append(akey)

        if len(results) == 0 and self.origin_id != self.id:
            return self.origin.get_actor_by_type(atype)
        else:
            if len(results) == 1:
                return results[0]
            else:
                return None

    def get_scoped_types(self, on_type, the_type):
        pass

    def get_applied_targets(self, ntype, context=None):

        #breaking to renew
        if True==False:

            if ntype.scope == 'event':
                # we are gonna check for elements
                # defined by this event only
                #
                # if we are looking up the invitation target
                # we should only concider the one of this event

                # if
                pass
            else:
                pass

        if True==True:
            print('APPLIED TARGETS ', ntype, ntype.scope, ' on ', self.get_display())

            suffix = 'items'
            if ntype.reference == 'actor':
                suffix = 'actors'
            elif ntype.reference == 'target':
                suffix = 'targets'

            if ntype.scope == 'children':
                typed = self.related.parent.do_query('query_children_'+ntype.name)
            elif ntype.scope == 'descendants':
                typed = self.related.get_root().do_query('query_descendants_'+ntype.name)
            else:
                if ntype.reference == 'context':
                    typed = self.do_query('query_all_'+ntype.name)
                else:
                    typed = self.do_query('query_this_'+ntype.name)

            #print('--> ', typed)

            return typed

        if context == None:
            context = self.context

        base_mods = Moderation.objects.all()#status=ntype.status.name)

        if ntype.reference == 'context':
            pass
        else:
            base_mods = base_mods.filter(context=context)

            type_related = []
            type_related.append( (Q(id=self.id) | Q(origin_id=self.id) ) )

            #if ntype.type.reference == 'related':
            #    type_related.append( Q(related_id=self.related_id) )
            if ntype.scope != 'event':
                type_related.append( Q(related_id=self.related_id) )

            # is this type herited ?
            if ntype.scope == 'descendants':
                # is the an ancestor with this type.type ?
                for ancestor in self.related.get_ancestors():
                    if ntype.type in ancestor.get_infered_types():
                        # okay, this type applies from here to the descendants
                        type_related.append( Q(related_id=ancestor.related_id) )
                        # = Q(related__in=self.get_ancestors(include_self=True))

            elif ntype.scope == 'children':
                if ntype.type in self.related.parent.get_infered_types():
                    type_related.append( Q(related_id=parent.related_id) )
                    #Q(related__in=(self.parent, self.related))

            base_mods = base_mods.filter( Q(reduce(operator.or_, type_related)) )


        mods = base_mods.filter(status=ntype.status.name)

        from ilot.rules.models import Type
        if not ntype.id in Type.objects.overrides_statuses:
            overrides = Type.objects.filter(overrides=ntype, overrides__reference=ntype.reference)
            Type.objects.overrides_statuses[ntype.id] = list(overrides.values_list('status__name', flat=True))

        overrides_statuses = Type.objects.overrides_statuses[ntype.id]

        for overriding_status in overrides_statuses:

            if ntype.reference == 'target':
                # event is overloaded by following replace event
                exclude = Q( id__in=base_mods.filter(status=overriding_status).values_list('origin_id', flat=True) )

            elif ntype.reference == 'actor':
                exclude = Q( id__in=base_mods.filter(status=overriding_status).values_list('origin_id', flat=True) )

            elif ntype.reference == 'related':
                exclude = Q( id__in=base_mods.filter(status=overriding_status).values_list('related_id', flat=True) )

            elif ntype.reference == 'event':
                exclude = Q( id__in=base_mods.filter(status=overriding_status).values_list('origin_id', flat=True) )

            elif ntype.reference == 'context':
                exclude = Q( id__in=base_mods.filter(status=overriding_status).values_list('related_id', flat=True) )

            #type_base = type_base.exclude(exclude)
            #if overrides.count():
            #print('EXCLUDING', overriding_status, typed.count(), type_base.filter(exclude).count() )

            mods = mods.exclude(exclude)

            #print('EXLUDING mods ', type_base.filter(exclude).values_list('id'), )
            #print('EXCLUDED', overriding_status, typed.count(), type_base.filter(exclude).count() )


        if ntype.reference == 'actor':
            targets = mods.values_list('akey', flat=True).distinct()
        elif ntype.reference == 'target':
            targets = mods.values_list('target', flat=True).distinct()
        elif ntype.reference == 'related':
            targets = mods.values_list('related_id', flat=True).distinct()
        elif ntype.reference == 'event':
            targets = mods.values_list('id', flat=True).distinct()
        elif ntype.reference == 'context':
            targets = mods.values_list('context', flat=True).distinct()
        else:
            print('WRONG TARGET REFERENCE', ntype.reference)
            raise
        #print('--> TARGETS for', ntype, 'on', self.get_infered_types(), '\n ------------ ',targets)
        return targets


    def get_actor_infered_types(self, actor_id, save_types=False):
        return self.get_infered_types(actor_id, save_types=True)

    def get_my_infered_types(self):
        return self.get_actor_infered_types(request_switch.akey)

    def get_actor_infered_types(self, actor_id, save_types=False):
        return self.get_infered_types(actor_id, save_types=save_types)

    def get_infered_types(self, actor_id=None, save_types=False, replace=True, cached_ids=False):

        from ilot.rules.models import Type

        if not save_types and replace:
            if self.id in Item.objects.tree_infered_types:
                if str(actor_id) in Item.objects.tree_infered_types[self.id]:
                    if cached_ids:
                        return Item.objects.tree_infered_types[self.id][str(actor_id)]
                    return Type.objects.filter(id__in=Item.objects.tree_infered_types[self.id][str(actor_id)])

        if not self.id in Item.objects.tree_id_statuses or save_types:
            self._update_statuses()

        if replace and save_types and settings.CACHE_TYPED_LISTS:
            if self.id in Item.objects.tree_infered_types:
                for type_id in Item.objects.tree_infered_types[self.id]:
                    if type_id in Item.objects.tree_context_typed:
                        del Item.objects.tree_context_typed[type_id]

        #if self.id in Item.objects.tree_id_statuses:
        statuses = Item.objects.tree_id_statuses[self.id]
        #else:
        #    statuses = [self.status]

        # print('GET INFERED ', self.status)
        mods = None
        # if we check for the object on himself
        if not actor_id:
            # if we are on an item,
            if self.related_id == self.id:

                #mods = Moderation.objects.filter(related_id=self.related_id)
                #statuses = mods.values_list('status', flat=True).distinct()

                # the applying types are those with item reference
                types = Type.objects.filter(reference__in=('related', 'context', 'clone'))
                types = types.filter(status__name__in=statuses)

                qtypes = []

                # we only select those extending the item origin types
                # Ex: Project > Initiative > SubInitiative
                qtypes.append( Q(type__isnull=True) )
                qtypes.append( Q(type__status__name__in=statuses,
                                 type__reference__in=('related', 'context', 'clone')) )

                if self.related.parent_id:
                    qtypes.append( Q(type__in=self.related.parent.get_infered_types()) )

                if self.origin_id != self.id:
                    qtypes.append( Q(type__in=self.origin.get_infered_types(save_types=save_types)) )

                types = types.filter( Q(reduce(operator.or_, qtypes)) )
                #return types

            # else, the applying types are those with event set
            else:
                types = Type.objects.filter(reference__in=('event',)) #, 'related'
                qtypes = []
                # filter with event types
                if self.origin_id != self.id:
                    origin_types = self.origin.get_infered_types(replace=False)
                    related_types = self.related.get_infered_types(replace=False)
                    qtypes.append( Q(status__name__in=statuses, type__isnull=True) )
                    qtypes.append( Q(status__name__in=statuses, type__in=list(origin_types)) )
                    qtypes.append( Q(status__name__in=statuses, type__in=list(related_types)) )

                types = types.filter( Q(reduce(operator.or_, qtypes)) )

            # replace with next event types
            if replace:
                # okay we got the types of the object
                # they may be overriden by next events
                # we have to discard those overriden

                # we check for next events
                if self.related_id == self.id:
                    mods = Moderation.objects.filter(related_id=self.related_id)
                else:
                    mods = Moderation.objects.filter(related_id=self.related_id, origin_id=self.id)

                sub_statuses = list(mods.values_list('status', flat=True).distinct())

                if not self.related_id == self.id:
                    overriding_types = Type.objects.filter(Q(status__name__in=sub_statuses,
                                                             reference__in=('event', 'related'),
                                                             overrides__in=types,
                                                             type__in=types,))

                    types = types.exclude(id__in=overriding_types.values_list('overrides_id', flat=True))

                    # we also have to add these types
                    types = Type.objects.filter( Q(id__in=types)|Q(id__in=overriding_types) )

                else:
                    overriding_types = Type.objects.filter(overrides__in=types)
                    #if overriding_types.count():
                    # those overridden
                    overridden_types = Type.objects.filter(id__in=list(overriding_types.values_list('overrides_id', flat=True)) )
                    # mods with the overriden status that needs to be discarded
                    overridden_mods = mods.filter(status__in=list(overridden_types.values_list('status__name', flat=True)) )
                    # mods with the overriding status that discards
                    overriding_mods = mods.filter(status__in=list(overriding_types.values_list('status__name', flat=True)) )

                    #print('Actor ', actor_id, self.id)
                    #print( 'Overriding ', overridden_types, 'with', overriding_types )
                    #print( overridden_mods.count(), overriding_mods.count() )

                    diff = overridden_mods.exclude(id__in=overriding_mods.values_list('origin_id', flat=True))

                    #print('finale DIFF', diff, diff.values_list('status', flat=True), diff.values_list('target', flat=True) )

                    remaining_statuses = diff.values_list('status', flat=True)

                    types = types.exclude( id__in=list(overridden_types.exclude(status__name__in=remaining_statuses).values_list('id', flat=True) ) )
                    types = types.exclude( id__in=list(overriding_types.exclude(status__name__in=remaining_statuses).values_list('id', flat=True) ) )

                        #print('Final types', types)

                    #print('EXCLUDING:', self.status, sub_statuses, excluding_types, 'from', types)
                    #else:
                        #print('INCLUDED TYPES', types)
                    #types = types.exclude(Q(status__name__in=sub_statuses, reference='event', replaces=True,
                    #                        type__status__name=self.status, type__reference='event'))

            #direct_types = types.filter( Q(reduce(operator.or_, qtypes)) )

            # include this event descendants types
            #sub_events_statuses = Moderation.objects.filter(origin_id=self.id).values_list('status', flat=True)
            #sub_types = Type.objects.filter(replaces=True, type__in=direct_types, status__name__in=sub_events_statuses)
            #qtypes.append( Q(id__in=sub_types.values_list('id', flat=True)) )


        else:
            # we need to check if the actor
            # is the actual actor or target of some events
            # so ...
            # we get the statuses where target or actor is involved
            # if we are on an item,

            if self.related_id == self.id:
                mods = Moderation.objects.filter(related_id=self.related_id)
                scopes = ('descendants', 'children', 'item', 'event')
            else:
                mods = Moderation.objects.filter( Q(id=self.id)|Q(origin_id=self.id) )
                scopes = ('event', )

                #mods = Moderation.objects.filter(id=self.id)

            #actor_statuses = mods.filter(akey=actor_id).values_list('status', flat=True).distinct()
            #target_statuses = mods.filter(target=actor_id).values_list('status', flat=True).distinct()

            actor_statuses = None
            if self.id in Item.objects.tree_actor_statuses and not save_types:
                if actor_id in Item.objects.tree_actor_statuses[self.id]:
                    actor_statuses = Item.objects.tree_actor_statuses[self.id][actor_id]
            else:
                Item.objects.tree_actor_statuses[self.id] = {}

            if not actor_statuses:
                actor_statuses = mods.filter(akey=actor_id).values_list('status', flat=True).distinct()
                actor_statuses = Item.objects.tree_actor_statuses[self.id][actor_id] = list(actor_statuses)


            target_statuses = None
            if self.id in Item.objects.tree_target_statuses and not save_types:
                if actor_id in Item.objects.tree_target_statuses[self.id]:
                    target_statuses = Item.objects.tree_target_statuses[self.id][actor_id]
            else:
                Item.objects.tree_target_statuses[self.id] = {}

            if not target_statuses:
                target_statuses = mods.filter(target=actor_id).values_list('status', flat=True).distinct()
                target_statuses = Item.objects.tree_target_statuses[self.id][actor_id] = list(target_statuses)


            # print(target_statuses)

            # remove status from mods overriding ?

            # the types applying may be those
            # with the actor_id as actor
            # or with the actor_id as target

            # from these types
            # we only need thoses extending the object

            type_list = []
            if self.id != self.related_id:
                item_infered = self.related.get_infered_types(save_types=save_types, cached_ids=True)
                type_list.append( Q(status__name__in=actor_statuses, reference='actor', scope__in=scopes, type__in=item_infered) )
                type_list.append( Q(status__name__in=target_statuses, reference='target', scope__in=scopes, type__in=item_infered) )

            event_infered = self.get_infered_types(save_types=save_types, cached_ids=True)
            type_list.append( Q(status__name__in=actor_statuses, reference='actor', scope__in=scopes, type__in=event_infered) )
            type_list.append( Q(status__name__in=target_statuses, reference='target', scope__in=scopes, type__in=event_infered) )

            if self.origin_id != self.id:
                origin_infered = self.origin.get_infered_types(save_types=save_types, cached_ids=True)
                type_list.append( Q(status__name__in=actor_statuses, reference='actor', scope__in=scopes, type__in=origin_infered) )
                type_list.append( Q(status__name__in=target_statuses, reference='target', scope__in=scopes, type__in=origin_infered) )


            # how to filter for the event only roles ?
            # from the types
            # what are the event related roles ?
            # role_types = types.filter(scope='event')


            if replace:

                types = Type.objects.filter( Q(reduce(operator.or_, type_list)) )

                if self.related_id == self.id:
                    mods = Moderation.objects.filter( related_id=self.related_id )
                else:
                    mods = Moderation.objects.filter( Q(id=self.id)|Q(origin_id=self.id) )
                mods = mods.filter( Q(akey=actor_id)|Q(target=actor_id) )

                # exclude those where status are overridden
                # those that overrides
                overriding_types = Type.objects.filter(overrides__in=types)

                if overriding_types.count():
                    # those overridden
                    overridden_types = Type.objects.filter(id__in=list(overriding_types.values_list('overrides_id', flat=True)) )
                    # mods with the overriden status that needs to be discarded
                    overridden_mods = mods.filter(status__in=list(overridden_types.values_list('status__name', flat=True)) )
                    # mods with the overriding status that discards
                    overriding_mods = mods.filter(status__in=list(overriding_types.values_list('status__name', flat=True)) )

                    #print('Actor ', actor_id, self.id)
                    #print( 'Overriding ', overridden_types, 'with', overriding_types )
                    #print( overridden_mods.count(), overriding_mods.count() )

                    diff = overridden_mods.exclude(id__in=overriding_mods.values_list('origin_id', flat=True))

                    #print('finale DIFF', diff, diff.values_list('status', flat=True), diff.values_list('target', flat=True) )

                    remaining_statuses = diff.values_list('status', flat=True)

                    types = types.exclude( id__in=overridden_types.exclude(status__name__in=remaining_statuses).values_list('id', flat=True) )
                    types = types.exclude( id__in=overriding_types.exclude(status__name__in=remaining_statuses).values_list('id', flat=True) )

                    #print('Final types', types)

                    type_list = []
                    type_list.append( Q(id__in=types.values_list('id', flat=True)) )

                #types = types.filter( Q() Q(status__in=diff.values_list('status', flat=True)) |  )

                #types = types.exclude(id__in=overriding_types.values_list('overrides_id', flat=True))

                # we also have to add these types
                #types = Type.objects.filter( Q(id__in=types)|Q(id__in=overriding_types) )

                #replace = False


            #if self.origin_id != self.id:
            #    type_list.append( Q(id__in=self.origin.get_infered_types(actor_id, save_types=sub_save_types) ) )


            # actors herit of there own context types also
            #if actor_id != self.id:
            type_list.append( Q(id__in=Item.objects.get_at_id(actor_id).get_infered_types(save_types=save_types) ) )

            # actors herit of it's item roles also
            if self.related_id != self.id:
                type_list.append( Q(id__in=self.related.get_infered_types(actor_id, save_types=save_types) ,
                                    scope__in=('item', 'descendants', 'children') ) )

            # how do i check for herited types like owner ?
            # we can accumulate the types from the ancestors
            if self.related.parent:
                type_list.append( Q(id__in=self.related.parent.get_infered_types(actor_id, save_types=save_types) ,
                                    scope__in=('descendants', 'children') ) )

            types = Type.objects.filter( Q(reduce(operator.or_, type_list)) )

            #print('TYPES', self.id, types)




        if replace:

            if save_types and settings.CACHE_TYPED_LISTS:
                if self.id in Item.objects.tree_infered_types:
                    for type_id in Item.objects.tree_infered_types[self.id]:
                        if type_id in Item.objects.tree_context_typed:
                            del Item.objects.tree_context_typed[type_id]

            # update cached
            if not self.id in Item.objects.tree_infered_types:
                Item.objects.tree_infered_types[self.id] = {}

            if save_types and not actor_id:

                #if self.origin_id != self.id:
                #    Item.objects.tree_infered_types[self.origin_id] = {}

                if self.related_id != self.id:
                    Item.objects.tree_infered_types[self.related_id] = {}

                Item.objects.tree_actor_statuses[self.id] = {}
                Item.objects.tree_target_statuses[self.id] = {}

                #if self.origin_id != self.id:
                #    Item.objects.tree_actor_statuses[self.origin_id] = {}
                #    Item.objects.tree_target_statuses[self.origin_id] = {}

                if self.related_id != self.id:
                    Item.objects.tree_actor_statuses[self.related_id] = {}
                    Item.objects.tree_target_statuses[self.related_id] = {}

            # reset the actor types
            if save_types and not actor_id:
                Item.objects.tree_infered_types[self.id] = {}

            Item.objects.tree_infered_types[self.id][str(actor_id)] = list(types.values_list('id', flat=True).distinct())
            #print('UPDATED TYPES on ', self.id, self.status, actor_id, self.get_data())
        else:
            return types

        if cached_ids:
            return Item.objects.tree_infered_types[self.id][str(actor_id)]
        return Type.objects.filter(id__in=Item.objects.tree_infered_types[self.id][str(actor_id)])


    def get_important_actions(self):

        return self.get_actions().exclude(meta_type='request')



    def get_actions(self, profile=None):

        from ilot.rules.models import Rule, Action

        actor_id = request_switch.akey
        if self.id in Rule.objects.item_actor_actions \
            and actor_id in Rule.objects.item_actor_actions[self.id]:

            return Rule.objects.item_actor_actions[self.id][actor_id]

        rules = Rule.objects.filter(enabled=True).filter(type__in=self.get_infered_types(),
                                                         actor__in=self.get_my_infered_types())

        denied_rules = rules.filter(is_allowed=False)
        rules = rules.exclude( action_id__in=list(denied_rules.values_list('action_id', flat=True).distinct()) )

        if not self.id in Rule.objects.item_actor_actions:
            Rule.objects.item_actor_actions[self.id] = {}

        Rule.objects.item_actor_actions[self.id][actor_id] = Action.objects.select_related().filter( Q(id__in=rules.values_list('action', flat=True).distinct()) )
        return Rule.objects.item_actor_actions[self.id][actor_id]

        # append link permissions
        from ilot.models import Authorization
        als = Authorization.objects.filter(organization=request_switch.organization, akey=request_switch.akey, item=self.id, enabled=True).values_list('action', flat=True).distinct()

        return Action.objects.filter( Q(id__in=rules.values_list('action', flat=True).distinct())|Q(name__in=als) )

    def get_action_names(self):
        from ilot.rules.models import Rule, Action
        actor_id = request_switch.akey
        if self.id in Rule.objects.item_actor_action_names:
            if actor_id in Rule.objects.item_actor_action_names[self.id]:
                return Rule.objects.item_actor_action_names[self.id][actor_id]
        else:
            Rule.objects.item_actor_action_names[self.id] = {}
        Rule.objects.item_actor_action_names[self.id][actor_id] = list(self.get_actions().values_list('name', flat=True))
        return Rule.objects.item_actor_action_names[self.id][actor_id]


    def full_clean(self, exclude=None, validate_unique=True):

        if not exclude:
            exclude = []

        if not 'related' in exclude:
            exclude.append('related')
        if not 'origin' in exclude:
            exclude.append('origin')

        super(Moderation, self).full_clean(exclude=exclude, validate_unique=validate_unique)


    def save(self, *args, **kwargs):
        if 'using' in kwargs:
            return super(Moderation, self).save(*args, **kwargs)

        super(Moderation, self).save(*args, **kwargs)
        self._saved = True
        try:
            self._update_statuses()
            self.invalidate_infered_cache()

            from ilot.rules.models import Rule, Action

            if self.origin_id in Rule.objects.item_actor_actions:
                del Rule.objects.item_actor_actions[self.origin_id]
            if self.origin_id in Rule.objects.item_actor_action_names:
                del Rule.objects.item_actor_action_names[self.origin_id]

            if self.related_id in Rule.objects.item_actor_actions:
                del Rule.objects.item_actor_actions[self.related_id]
            if self.related_id in Rule.objects.item_actor_action_names:
                del Rule.objects.item_actor_action_names[self.related_id]

            self.origin.update_infered_types(self)

            #if self.related_id != self.id:
            #    self.related.update_infered_types(self)
            #if self.origin_id != self.id:
            #    self.origin.update_infered_types(self)
            #self.save_infered_types()
        except:
            for key in list(Item.objects.tree_id_statuses.keys()):
                del Item.objects.tree_id_statuses[key]
            for key in list(Item.objects.tree_infered_types.keys()):
                del Item.objects.tree_infered_types[key]
            traceback.print_exc()
            raise


    def invalidate_infered_cache(self):

        if True == False:
            for key in list(Item.objects.tree_id_statuses.keys()):
                del Item.objects.tree_id_statuses[key]
            for key in list(Item.objects.tree_infered_types.keys()):
                del Item.objects.tree_infered_types[key]

            if self.id in Item.objects.tree_infered_types:
                del Item.objects.tree_infered_types[self.id]
            if self.id in Item.objects.tree_id_statuses:
                del Item.objects.tree_id_statuses[self.id]

            if self.__inited__:
                for children in self.related.get_children():
                    children.invalidate_infered_cache()

    def update_infered_types(self, new_origin, recurse=True):
        """
        When the event is saved,
        it changes the related_id meta_types,
        the target meta_types, the actor meta_types, the context meta_types

        it also applies to the dependant types so it needs to propagate to the children types
        """
        #print('UPDATING TYPES '+self.status+' from ', self.get_infered_types(), self.related.get_infered_types())
        ref_self = new_origin

        status = new_origin.status

        # update the event itself
        current_types = self.get_infered_types()
        this_types = self.get_infered_types(save_types=True)


        # invalidate descendants infered cache
        # we should save notification to be sent too to other notified actors and targets
        type_scopes = []
        from ilot.grammar.models import Notification
        from ilot.meta.models import ActorInferedType, ActorNotification

        type_scopes.append( Q(type__in=current_types) )

        #if self.origin_id != self.id:
        #    type_scopes.append( Q(type__in=self.origin.get_infered_types()) )

        if self.related_id != self.id:
            type_scopes.append( Q(type__in=self.related.get_infered_types()) )

            #if self.related.parent_id:
            #    type_scopes.append( Q(type__in=self.related.parent.get_infered_types()) )

        notification_rules = Notification.objects.filter(status__name=status).filter( Q(reduce(operator.or_, type_scopes)) )

        print('RULES', this_types, status, notification_rules)

        for nrule in notification_rules:

            print('--> SHOULD NOTIFY ', nrule.type.reference, nrule)

            targets = new_origin.get_typed(nrule.target, scoped=True, from_event_id=new_origin.id)

            print('REF', nrule.target, 'TARGETS on ', nrule.type, targets)

            #targets = new_origin.get_applied_targets(nrule.target)

            #print(' TARGETS ', nrule.target, 'on', new_origin.get_infered_types(), targets)


            ref = new_origin

            # for each actor
            for actor in targets:
                #
                #actor = actor.id
                if not ref.id in Item.objects.tree_actor_infered_types:
                    Item.objects.tree_actor_infered_types[ref.id] = {}
                if not actor in Item.objects.tree_actor_infered_types[ref.id]:
                    Item.objects.tree_actor_infered_types[ref.id][actor] = {}
                if not nrule.target.id in Item.objects.tree_actor_infered_types[ref.id][actor]:
                    # save the actor role if not exists
                    try:
                        ninf = ActorInferedType.objects.get(context_id=ref.id, actor_id=actor, type=nrule.target)
                    except ActorInferedType.DoesNotExist:
                        ninf = ActorInferedType(context_id=ref.id, actor_id=actor, type=nrule.target, event_id=new_origin.id)
                        ninf.save()
                    Item.objects.tree_actor_infered_types[ref.id][actor][nrule.target.id] = ninf

                ninf = Item.objects.tree_actor_infered_types[ref.id][actor][nrule.target.id]

                notif = ActorNotification(context=ninf, rule=nrule, event=new_origin)
                notif.save()

                print('------- NOTYFIED ', actor, ' about ', ref.id)

        print('UPDATED NOTIFICATIONS ', status, this_types, notification_rules)


def upload_to(instance, filename):
    """
    Path and filename to upload to
    """
    #print('uploading to '+instance.get_path()+'.'+filename)
    #return instance.get_path()+'.'+filename
    filename, ext = os.path.splitext(filename)

    folder = hashlib.md5(request_switch.organization.id.encode('utf-8')).hexdigest()
    filename = hashlib.md5((instance.id).encode('utf-8')).hexdigest()
    return folder+'/'+filename+ext.lower()

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

class Translation(Moderation, GantChartMixin):
    """
    Namespaced fields
    """
    #
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    #
    #slug = models.CharField(max_length=128, blank=True, null=False)
    #label = models.CharField(max_length=65, blank=True, null=False)
    #title = models.CharField(max_length=156, blank=True, null=False)
    #description = models.TextField(blank=True, null=False)
    #
    parent = models.ForeignKey('core.Item', editable=True, blank=True, null=True, db_constraint=False, on_delete=models.CASCADE)

    #
    template = models.CharField(max_length=36, blank=True, default='')
    content = models.TextField(blank=True, null=False)

    def get_path(self):
        parts = []
        for ancestor in self.related.get_ancestors(include_self=False):
            parts.append(ancestor.get_translation(self.locale).slug)
        parts.append(self.slug)
        return '/'.join(parts)

    #def get_url(self, locale=None):
    #    return self.related.get_url(locale=locale)

    def full_clean(self, *args, **kwargs):

        return super(Translation, self).full_clean(*args, **kwargs)

        # check for correct slug
        if not self.slug and self.label:
            #if self.label == self.title and self.label:
            #    self.slug = slugify(self.label)
            #else:
            self.slug = slugify(self.label)

        elif not self.slug and self.title:
            self.slug = slugify(self.title)
        if not self.slug:
            self.slug = self.id
        # check that slug is unique within parent
        slugs = Translation.objects.filter(slug=self.slug, related__parent_id=self.related.parent_id)
        if slugs.count():
            scount = slugs.exclude(related_id=self.related_id, visible=True).count()
            if scount:
                self.slug = self.slug+str(scount)

                #raise ValidationError([
                #    ValidationError('Slug needs to be unique within parent', code='invalid', params={'value': self.slug})
                #])

        return super(Translation, self).full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if 'using' in kwargs:
            return super(Translation, self).save(*args, **kwargs)

        # check for correct slug
        if True == False:
            if not self.slug:
                if self.label == self.title and self.label:
                    self.slug = slugify(self.label)
                else:
                    self.slug = slugify(self.label+'-'+self.title)

        if self.related_id in Item.objects.tree_versions:
            del Item.objects.tree_versions[self.related_id]

        super(Translation, self).save(*args, **kwargs)


    def __unicode__(self):
        return self.slug+' - '+self.locale

    def get_template(self):
        if self.template:
            try:
                return Item.objects.get_at_id(self.template)
            except ObjectDoesNotExist:
                #return self.get_type()
                if self.get_type() != self:
                    return self.get_type().get_template()
                return self
        elif self.content:
            return self
        return self.get_type()

class ItemQuerySet(QuerySet):
    """
    Hack on query set fetch to get nodes from the instance cache
    """
    __cached__ = None

    def iterator(self):
        """
        An iterator over the results from applying this QuerySet to the
        database.
        """
        if self.__cached__:
            results = self.__cached__
        else:
            db = self.db
            compiler = self.query.get_compiler(using=db)
            # Execute the query. This will also fill compiler.select, klass_info,
            # and annotations.
            results = compiler.execute_sql()

        select, klass_info, annotation_col_map = (compiler.select, compiler.klass_info,
                                                  compiler.annotation_col_map)
        if klass_info is None:
            return
        model_cls = klass_info['model']
        select_fields = klass_info['select_fields']
        model_fields_start, model_fields_end = select_fields[0], select_fields[-1] + 1

        init_list = [f[0].target.attname for f in select[model_fields_start:model_fields_end]]

        if len(init_list) != len(model_cls._meta.concrete_fields):
            init_set = set(init_list)
            skip = [f.attname for f in model_cls._meta.concrete_fields
                    if f.attname not in init_set]
            model_cls = deferred_class_factory(model_cls, skip)

        for row in compiler.results_iter(results):
            if row[0] in Item.objects.tree_cache:
                obj = Item.objects.tree_cache[row[0]]
            else:
                obj = Item.objects.get_at_id(row[0])
                #obj = model_cls.from_db(db, init_list, row[model_fields_start:model_fields_end])
                #Item.objects.assign_tree_cache(obj)
            yield obj

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self.iterator())
            i = 0
            for row in self.query.get_compiler(self.db).results_iter():
                if not isinstance(row, Item):continue

                if not row[0] in Item.objects.tree_cache:
                    Item.objects.assign_tree_cache(self._result_cache[i])

                self._result_cache[i] = Item.objects.tree_cache[row[0]]

                #if 'translations' in self._result_cache[i]:
                #    del self._result_cache[i]['translations']

                if not row[0] in Item.objects.tree_results:
                    Item.objects.tree_results[row[0]] = list()

                Item.objects.tree_results[row[0]].append((self, i))
                i+=1

        if self._prefetch_related_lookups and not self._prefetch_done:
            self._prefetch_related_objects()

class TreeManager(Manager):

    tree_cache = object_tree_cache
    tree_map = ObjectTree()
    tree_results = ObjectTree()
    tree_times = ObjectTree()

    tree_images = {}

    tree_infered_types = {}
    tree_actor_infered_types = {}
    tree_id_statuses = {}
    tree_authorizations = {}

    tree_notif_rules = {}

    tree_actor_statuses = {}
    tree_target_statuses = {}

    tree_context_typed = {}

    tree_versions = {}

    tree_mods = {}

    tree_id_data = {}

    def get_query_set(self):
        return ItemQuerySet(model=self.model)

    def get_clean_path(self, url):
        if url in ('', '/', None):
            return ''
        url = unquote(url)
        # filter out possible parameters
        cleanUrl = url.split( '?' )[0]
        # handle possible anchor
        cleanUrl = cleanUrl.split( '#' )[0]
        # remove possible start slash
        while cleanUrl[0] == '/':
            cleanUrl = cleanUrl[1:]
        # remove possible end slash
        while cleanUrl[-1:] == '/':
            cleanUrl = cleanUrl[:-1]
        return cleanUrl

    def get_at_id(self, uid):
        if uid in Item.objects.tree_cache:
            return Item.objects.tree_cache[uid]
        else:
            item = Item.objects.get(id=uid)
            Item.objects.assign_tree_cache(item)
            return item

    def get_at_url(self, url, exact=True):
        item = None
        cleanUrl = self.get_clean_path(url)
        if cleanUrl in Item.objects.tree_cache:
            return Item.objects.tree_cache[cleanUrl]
        items = Item.objects.filter(id=cleanUrl).order_by('-ref_time')[:1]
        item = None
        if items.count() > 0:
            item = items[0]
        else:
            parts = cleanUrl.split('/')
            qdict = []
            n = 0
            for n in range(len(parts)):
                if n == len(parts)-1:
                    f = 'slug'
                else:
                    f = ('parent__'*(len(parts)-n-1))+'slug'

                qdict.append({f:parts[n]})
            try:
                from functools import reduce
            except:
                pass
            qgroup = reduce(operator.and_, (Q(**sv) for sv in qdict))
            try:
                item = Item.objects.filter(qgroup)[:1][0]
            except:
                raise ObjectDoesNotExist

        #self.assign_tree_cache(item)
        return item

    def update_tree_qs(self, item):

        id = item.id
        if id in self.tree_results:
            print('UPDATE ID', id)
            for qs, i in self.tree_results[id]:
                if qs and qs._result_cache:
                    print('REPLACING', qs._result_cache[i].label)
                    print('BY', self.tree_cache[id].label)
                    qs._result_cache[i] = self.tree_cache[id]
                    if 'translations' in self.tree_cache[id]:
                        del self.tree_cache[id]['translations']

    def assign_tree_cache(self, item):

        # TODO
        # check for cache size !
        id = item.id
        if id in self.tree_cache:
            return

        if not isinstance(item, Item):
            raise

        for key in ('children_qs', 'children_count', 'translations', 'descendants_qs', 'descendants_self_qs', 'descendants_count'):
            if key in item.__cache__:
                del item.__cache__[key]

        self.tree_cache[id] = item
        self.tree_map[id] = (id,)

        if item.parent:
            Item.objects.update_tree_qs(item)

        #print('ADD CACHE ', item, id)

    def remove_tree_cache(self, item, using=None):
        return
        #print('REMOVING CACHED ', self.tree_map.__get_db__(), self.tree_map[item.id])
        for key in ('children_qs', 'children_count', 'translations', 'descendants_qs', 'descendants_self_qs', 'descendants_count'):
            if key in item.__cache__:
                del item.__cache__[key]
        for p in self.tree_map[item.id]:
            self.tree_cache.remove(p)
        #print(self.tree_map.__get_db__(), self.tree_map[item.id])
        self.tree_map.remove(item.id)

    def get_or_create_url(self, url, **kwargs):
        # filter out possible parameters
        if not url:
            raise ObjectDoesNotExist
        item = None
        cleanUrl = self.get_clean_path(url)
        try:
            item = Item.objects.get_at_url(cleanUrl, exact=True)
            if item.get_path() == cleanUrl:
                return item
        except:
            pass

        # split url
        parts = cleanUrl.split('/')
        baseItem = None
        if len(parts) == 1:
            slug = parts[0]
            item = self.create_item('', parts[0], cleanUrl, **kwargs)
        else:
            basePath = ''
            for part in parts[:-1]:
                basePath = basePath+'/'+part
                parent = self.get_or_create_url(basePath, **kwargs)
            item = self.create_item(parent.id, parts[-1], cleanUrl, **kwargs)
        #Item.objects.assign_tree_cache(item)
        return item


class Item(Translation):
    """
    The model for an item
    """
    __cache__ = {}

    def __str__(self):
        return self.id

    def __unicode__(self):
        return self.id

    objects = TreeManager()

    __localizable__ = [#'slug',
                        #'label',
                        #'title',
                        #'description',
                        #'type',
                        'parent',
                        'content',
                        'template',
                        'order'
                        ]

    def __init__(self, *args, **kwargs):

        super(Item, self).__init__(*args, **kwargs)

        Item.objects.tree_cache[self.id] = self

        self.__inited__ = True
        self.__status__ = self.status
        self.get_data()
        self.get_cache_data()

    class Meta:
        ordering = ('order',)


    def __getattribute__(self, attr):

        # avoid looping on attributes
        if attr in ('get_data', '_data', '__cache__', '__localizable__', '__inited__', '__dict__'):
            return super(Item, self).__getattr__(attr)

        if attr in ('parent',):
            if self.parent_id and self.parent_id != self.id:
                return Item.objects.get_at_id(self.parent_id)
            else:
                return None

        elif attr in ('related',):
            return self

        elif attr in ('origin',):
            return super(Item, self).__getattr__(attr)

            if self.origin_id == self.id:
                return self

            if not self.origin_id in Item.objects.tree_mods:
                try:
                    Item.objects.tree_mods[self.origin_id] = Moderation.objects.get(id=self.origin_id)
                except ObjectDoesNotExist:
                    Item.objects.tree_mods[self.origin_id] = super(Item, self).__getattr__(attr)

            return Item.objects.tree_mods[self.origin_id]

        elif attr in self.__dict__:
            return self.__dict__[attr]

        elif attr in super(Item, self).__dict__:
            return super(Item, self).__dict__[attr]

        elif self.__inited__ and attr in self.__localizable__:
            trans = self.get_translation()
            if self.__class__ == trans.__class__:
                return super(Item, self).__getattr__(attr)
            else:
                return trans.__getattribute__(attr)

        elif self._data and attr in self._data:
            return self._data[attr]

        else:
            return super(Item, self).__getattribute__(attr)


    def __getattr__(self, key):

        if key in ('parent',):
            if self.parent_id:
                return Item.objects.get_at_id(self.parent_id)

        if key in ('related',):
            try:
                return Item.objects.get_at_id(self.id)
            except:
                return super(Item, self).__getattr__(key)

        if key in ('origin',):
            if self.origin_id in Item.objects.tree_mods:
                return Item.objects.tree_mods[self.origin_id]
            else:
                return super(Item, self).__getattr__(key)

        return super(Item, self).__getattr__(key)


    def __setattr__(self, attr, value):

        if self.__inited__ and attr in self.__localizable__:
            trans = self.get_translation()
            if self.__class__ == trans.__class__:
                return super(Item, self).__setattr__(attr, value)
            else:
                return trans.__setattr__(attr, value)

            #if self.locale == get_locale_as_organization():
            #    return super(Item, self).__setattr__(attr, value)

            #if self.locale != get_locale_as_organization():
                #if trans.id != self.id:
                # mark translation as dirty
            #    trans = self.get_translation()
            #    trans.__setattr__(attr, value)
            #else:
            #    return super(Item, self).__setattr__(attr, value)
        else:
            return super(Item, self).__setattr__(attr, value)


    def get_cache_data(self):

        if not self.__inited__:
            return self.__cache__

        #if self._state.db != Item.objects.tree_cache.__get_db__():
        #    print('DB mismatch')
        #    return self

        if self.parent_id and not self.parent_id in object_tree_cache:
            self.parent.set_cache_data()

        if not self.id in object_tree_cache:
            self.set_cache_data()

        return object_tree_cache[self.id].__cache__

    def set_cache_data(self):

        #print('XXXXXXXXXXX - data caching ', Item.objects.tree_cache.__get_db__(), self.id)

        Item.objects.update_tree_qs(self)

        if self.parent_id and not self.parent_id in object_tree_cache:
            self.parent.set_cache_data()

        #if not self.id in object_tree_cache:
        Item.objects.assign_tree_cache(self)

        if 'translations' in self.__cache__:
            del self.__cache__['translations']

        if self.parent_id and 'children_qs' in object_tree_cache[self.parent_id].__cache__:
            object_tree_cache[self.parent_id].__cache__['children_qs']._result_cache = None
            del object_tree_cache[self.parent_id].__cache__['children_qs']

        if not object_tree_cache[self.id].__cache__:
            object_tree_cache[self.id].__cache__ = {}

        if self.__inited__:
            # here is indexing
            pass

        return self


    def delete(self, *args, **kwargs):

        # purge caches
        if self.parent_id and self.parent_id in object_tree_cache:
            Item.objects.remove_tree_cache(self.parent)

        if self.id in object_tree_cache:
            Item.objects.remove_tree_cache(self)

        super(Item, self).delete(*args, **kwargs)

    def full_clean(self, *args, **kwargs):

        if not self.related_id:
            self.related_id = self.id

        return super(Item, self).full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):

        if not self.related_id:
            self.related_id = self.id

        if 'using' in kwargs:
            return super(Item, self).save(*args, **kwargs)

        if self.parent_id == self.id:
            self.parent_id = None

        self.full_clean()

        self.related_id = self.id

        # save translation if not saved
        #if self.locale != get_locale_as_organization():
        #    self.get_translation().save(*args, **kwargs)

        super(Item, self).save(*args, **kwargs)

        if not 'using' in kwargs:
            # purge caches
            if self.id in object_tree_cache and 'translations' in object_tree_cache[self.id].__cache__:
                t_data = object_tree_cache[self.id].__cache__
                del t_data['translations']

            if self.parent_id and self.parent_id in object_tree_cache and self.get_field_diff('parent_id'):
                if 'descendants_qs' in object_tree_cache[self.parent_id].__cache__:
                    object_tree_cache[self.parent_id].__cache__['descendants_qs']._result_cache = None
                    del object_tree_cache[self.parent_id].__cache__['descendants_count']
                if 'descendants_self_qs' in object_tree_cache[self.parent_id].__cache__:
                    object_tree_cache[self.parent_id].__cache__['descendants_self_qs']._result_cache = None
                    del object_tree_cache[self.parent_id].__cache__['descendants_count']
                if 'children_qs' in object_tree_cache[self.parent_id].__cache__:
                    object_tree_cache[self.parent_id].__cache__['children_qs']._result_cache = None
                    del object_tree_cache[self.parent_id].__cache__['children_count']

            if self.parent_id and self.parent_id in object_tree_cache:
                Item.objects.remove_tree_cache(self.parent)
            if self.id in object_tree_cache:
                Item.objects.remove_tree_cache(self)
            self.set_cache_data()


    def get_root(self):
        return self.get_ancestors(include_self=True)[0]

    def is_visible(self):
        return self.visible

    def get_path(self):
        parts = []
        for ancestor in self.get_ancestors(include_self=True):
            parts.append(ancestor.slug)
        return '/'.join(parts)


    def get_ancestors(self, ascending=None, include_self=False):

        if self.parent_id == self.id:
            self.parent_id = None
            self.parent = None

        if not self.parent_id:
            if include_self == True:
                return [self]
            else:
                return []

        if self.parent_id == None or self.parent_id == self.id:
            if include_self:
                return [self]
            else:
                return []
        else:
            ac = 0
            if include_self:
                ancestors = [self]
            else:
                ancestors = []
            a = self
            while a.parent and a.parent_id and not a.parent in ancestors and ac < 10:
                ancestors.append(a.parent)
                a = a.parent
                ac += 1
                if not a.parent:
                #    ancestors.append(a)
                    break
            #return ancestors
            return list(reversed(ancestors))

            ancestors = self.parent.get_ancestors()
            ancestors.append(self.parent)
            if include_self:
                ancestors.append(self)
            return ancestors

    def get_descendants(self, depth=5, include_self=False):
        """
        Get all the descendants items
        """
        node_data = self.get_cache_data()

        if include_self == True:
            cache_key = 'descendants_self_qs'
        else:
            cache_key = 'descendants_qs'
        cache_descendants = False
        if not cache_key in node_data or cache_descendants:
            qs = Item.objects.get_query_set()
            parent_keys = ['parent_id']
            parent_key = 'parent_id'
            parent_dict = {parent_key:self.id}
            i = 0
            while Item.objects.filter(**parent_dict).exists():
                parent_key = 'parent__'+parent_key
                parent_dict = {parent_key:self.id}
                parent_keys.append(parent_key)
                if i == 4:
                    break
                else:
                    i+=1
            try:
                from functools import reduce
            except:
                pass
            qgroup = reduce(operator.or_, (Q(**{fieldname: self.id}) for fieldname in parent_keys))
            if include_self:
                qs = qs.filter(qgroup|Q(id=self.id), visible=True)
            else:
                qs = qs.filter(qgroup, visible=True)
                node_data['descendants_count'] = qs.count()

            return qs
            #node_data[cache_key] = qs

        return node_data[cache_key]

    def get_descendants_count(self):
        if not self.id in object_tree_cache \
            or not 'descendants_qs' in object_tree_cache[self.id]:
            self.get_descendants()
        return object_tree_cache[self.id]['descendants_count']

    def get_children(self):
        """
        Returns the children QS
        """
        node_data = self.get_cache_data()

        if not 'children_qs' in node_data:
            node_data['children_qs'] = Item.objects.filter(parent_id=self.id, visible=True).order_by('order')

        if not 'children_count' in node_data:
            node_data['children_count'] = node_data['children_qs'].count()

        return node_data['children_qs']

    def get_children_count(self):
        #if self._state.db != request_switch.organization.id:
        #    self.get_children()
        if not self.id in object_tree_cache \
            or not 'children_count' in object_tree_cache[self.id].__cache__:
            self.get_children()
        return object_tree_cache[self.id].__cache__['children_count']

    def is_leaf_node(self):
        return self.get_children_count() == 0

    def get_translation(self, locale=None):
        try:
            return self.get_translations()[0]
        except IndexError:
            return self

    def get_translations(self):
        if not self.id in Item.objects.tree_versions:
            Item.objects.tree_versions[self.id] = Translation.objects.filter(related_id=self.id, visible=True).order_by('-ref_time')
        return Item.objects.tree_versions[self.id]

    def get_data(self, refresh=False):
        data = super(Item, self).get_data(refresh=refresh)
        for trans in reversed(self.get_translations()):
            data.update(trans.get_data(refresh=refresh))
        self._data = data
        return data

    def get_public_url(self, locale=None):
        return '/'+self.get_path().replace('/', '-')+'.html'

    def get_absolute_url(self):
        return self.get_url()
