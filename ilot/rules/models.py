from ilot.core.models import AuditedModel
from ilot.core.models import request_switch
from django.db.models.fields import CharField, BooleanField, EmailField, \
                                    IntegerField, TextField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db import models
from django.db.models.fields.files import ImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

from django.db.models.query_utils import Q

from django.contrib import messages

import os
import hashlib

EXT = (
    (None, 'All available formats'),
    ('/', 'Backend HTML'),
    ('.html', 'Public HTML'),
    ('.json', 'JSON'),
    ('.email', 'Email'),
    ('.txt', 'TXT'),
    ('.md', 'Markdown')
)

METHOD = (
    (None, 'All methods'),
    ('GET', 'GET/SUB'),
    ('POST', 'POST/PUB')
)

META_TYPES = (
    ('item', 'Item'),
    ('version', 'Version'),
    ('event', 'Event'),
    ('request', 'Request'),
    ('context', 'Context'),
    ('clone', 'Clone'),
    ('actor', 'Actor')
)

TARGETS = (
    ('item', 'Item (Shared)'),
    ('actor', 'Actor (Private)'),
    ('origin_actor', 'Origin Actor'),
    ('origin_target', 'Origin Target'),
    ('origin_related', 'Origin Item'),
    ('any', 'Must be defined in attributes'),
)

PARENTS = (
    ('origin', 'Origin Related'),
    ('root', 'Origin Related Root'),
    ('none', 'New Root'),
    ('anything', 'Anything (Choosen in action)'),
)


class Status(AuditedModel):
    name = CharField(max_length=36, unique=True)
    description = CharField(max_length=4096, default='', blank=True)

    #
    shared = BooleanField(default=False, verbose_name='Share with all interfaces')
    #
    silent = BooleanField(default=False, verbose_name='Silence status in feeds')

    def __str__(self):
        return str(self.name)
    class Meta:
        ordering = ['name']



class Action(AuditedModel):

    package = ForeignKey('ilot.Package', blank=True, null=True,
                         related_name='actions', verbose_name='Package',
                         db_constraint=False, 
                         on_delete=models.PROTECT)

    name = CharField(max_length=36, unique=True, help_text="Action keyword")
    description = CharField(max_length=4096, default='', blank=True, null=True)
    # intended status
    status = ForeignKey(Status, related_name='actions', blank=True, null=True,
                        db_constraint=False, on_delete=models.PROTECT)
    #
    meta_type = CharField(max_length=36, default='event', choices=META_TYPES)
    #
    #target_auto = CharField(max_length=36, default='actor', choices=TARGETS)
    #target = ForeignKey sur le type de l'origin ...
    target_type = ForeignKey('rules.Type', related_name='targets',
                             blank=True, null=True,
                             verbose_name="Target must be ",
                             db_constraint=False, on_delete=models.PROTECT)

    #
    authorize = BooleanField(default=False,
                             verbose_name="Request external callback")
    signed = BooleanField(default=False,
                             verbose_name="Request signature")
    transaction = BooleanField(default=False,
                             verbose_name="Request transaction")

    #
    behavior = ForeignKey('self', related_name='behaviors',
                          blank=True, null=True, verbose_name="Request behavior ",
                          db_constraint=False, on_delete=models.PROTECT)
    #
    webhook = ForeignKey('webhooks.Webhook', blank=True, null=True,
                         related_name='actions', verbose_name='Webhook',
                         db_constraint=False, on_delete=models.PROTECT)


    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['package', 'meta_type', 'name']

    def save(self, *args, **kwargs):
        """
        Update the data action flag
        """
        return super(Action, self).save(*args, **kwargs)

        name_changed = self.get_field_diff(name)
        if name_changed:
            from ilot.core.models import DataPath
            mods = Moderation.objects.filter(action=self.name).update()
            for mod in mods:
                mod.save_infered_types()



    def get_panel(self):
        from ilot.grammar.models import Panel
        try:
            return Panel.objects.get(action_id=self.id)
        except Panel.DoesNotExist:
            print('Missing panel')
            panel = Panel(action=self)
            panel.save()
            return panel


REFERENCES = (
    ('event', 'Event'),
    ('actor', 'Actor'),
    ('target', 'Target'),
    ('related', 'Item'),
    ('context', 'Context'),
)#('origin', 'Origin'),


def upload_to(instance, filename):
    """
    Path and filename to upload to
    """
    #print('uploading to '+instance.get_path()+'.'+filename)
    #return instance.get_path()+'.'+filename
    filename, ext = os.path.splitext(filename)

    folder = hashlib.md5(request_switch.organization.id.encode('utf-8')).hexdigest()
    filename = hashlib.md5((instance.id+str(instance.version)).encode('utf-8')).hexdigest()

    return folder+'/'+filename+ext.lower()

SCOPES = (
          ('event', 'Event'),
          ('item', 'Item'),
          ('children', '+Children'),
          ('descendants', '+Descendants'),
         )


from django.db.models.manager import Manager

class TypeManager(Manager):

    overrides_statuses = {}


class Type(AuditedModel):

    package = ForeignKey('ilot.Package', blank=True, null=True,
                         related_name='types', verbose_name='Package',
                         db_constraint=False, on_delete=models.PROTECT)

    #
    type = ForeignKey('self', blank=True, null=True,
                      limit_choices_to=Q(  Q(reference='event')|Q(reference='related')|Q(reference='context')|Q(reference='target') ),
                      related_name='children_types', verbose_name='On a',
                       db_constraint=False, on_delete=models.PROTECT)

    status = ForeignKey(Status, related_name='types', verbose_name='A',
                        db_constraint=False, on_delete=models.PROTECT)

    reference = CharField(max_length=36, default='origin', choices=REFERENCES,
                          verbose_name='')
    #
    overrides = ForeignKey('self', blank=True, null=True,
                           related_name='overriding',
                           verbose_name='Overrides type',
                           db_constraint=False, on_delete=models.PROTECT)

    #
    name = CharField('is a', max_length=96, unique=True)
    scope = CharField('and applies to ', max_length=96, default='item', choices=SCOPES)

    image = ImageField(upload_to=upload_to, blank=True, null=True)

    """#
    avatar = ImageSpecField(source='image',
                            processors=[ResizeToFill(100, 100)],
                            format='PNG',
                            options={'quality': 60})
    thumbnail = ImageSpecField(source='image',
                            processors=[ResizeToFit(256, 256)],
                            format='PNG',
                            options={'quality': 60})
    """
    display_field = ForeignKey('rules.Attribute', blank=True, null=True,
                               related_name='display_fields',
                               db_constraint=False, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

    objects = TypeManager()

    def save(self, *args, **kwargs):
        return super(Type, self).save(*args, **kwargs)
        # TODO
        # rebuild the corresponding meta_types
        from ilot.core.models import Moderation
        mods = Moderation.objects.filter(status=self.status.name)
        for mod in mods:
            mod.save_infered_types()



    def get_ancestors(self):
        ancestors = []
        try:
            if self.type and self.type != self and self.type.reference in ('related', 'event', 'context', 'clone'):
                ancestors = self.type.get_ancestors()
            else:
                ancestors = []
            ancestors.append(self)
        except:
            print('ERROR IN TYPE CHAIN !!!!!!', self.type, self)
        return ancestors

    #a ContributionComment is a commented Contribution Event

DATATYPES = (
    ('string', 'string'),
    ('number', 'number'),
    ('integer', 'integer'),
    ('boolean', 'boolean'),
    ('array', 'array'),
    ('object', 'object')
)

DATATYPES = (
    ('string', 'string'),
    ('name', 'Name'),
    ('number', 'Number'),
    ('integer', 'Integer'),
    ('boolean', 'Boolean'),
    ('datetime', 'DateTime'),
    ('type', 'Type'),
    ('choice', 'Choice'),
)

DATATYPES = (
    ('string', 'Word'),
    ('title', 'Title (A sentence)'),
    ('description', 'Description (A text)'),
    ('markdown', 'Markdown (A markdown text)'),

    ('target', 'Target Selector'),
    ('query', 'Target Query'),

    ('image', 'Media Image'),

    ('datetime', 'DateTime chooser'),
    ('number', 'Number'),
    ('integer', 'Integer'),
    ('boolean', 'Boolean'),
    ('email', 'Email'),
    ('url', 'Url'),

    ('slug', 'Slug field (this-is-a-slug)'),

    ('parent', 'Parent Item (An item)'),
    ('start', 'Start Datetime (Core)'),
    ('end', 'End Datetime (Core)'),
)

# choice with other ...
# https://djangosnippets.org/snippets/863/

class Attribute(AuditedModel):

    # related action
    action = ForeignKey(Action, related_name='attributes', on_delete=models.PROTECT)
    # field name
    name = CharField(max_length=36)
    # field label
    label = CharField(max_length=36, default='', blank=True)
    #
    order = IntegerField(default=0)
    # field description
    description = TextField(default='', blank=True)
    # field help
    help = TextField(default='', blank=True)

    # is field required
    required = BooleanField(default=False)
    # is field visible
    hidden = BooleanField(default=False)
    # is field required
    unique = BooleanField(default=False)

    #
    datatype = CharField(max_length=36, default='string', choices=DATATYPES)
    #
    default = CharField(max_length=4096, default='', blank=True)
    #
    params = TextField(default='', blank=True)

    #
    regexp = CharField(max_length=4096, default='', verbose_name="Validation regexp", blank=True)
    regexp_error = TextField(default='', blank=True)

    # is field searchable
    searchable = BooleanField(default=False)
    # is field private
    private = BooleanField(default=False)
    # is field queryable
    queryable = BooleanField(default=False)

    def __str__(self):
        return str(self.action.name)+'.'+str(self.name)

    class Meta:
        ordering = ['order']

# TODO
# Uniformize models REFERE?NCE, scope etc ...

BRANCHES =(
    ('this', 'This'),
    ('target', 'Target'),
    ('origin', 'Origin'),
    ('actor', 'Actor'),
    ('related', 'Item'),
)

METHODS = (
    ('list', 'List'),
    ('total', 'Total'),
    ('count', 'Count'),
    ('value', 'Value')
)

#    this.self.amount.value
#    item.Budget.value.total

class Property(AuditedModel):
    """
    Property is a dynamique calculation of item property

    if you need to get a value you have to be sure that only one result is obtained
    otherwise this will raise an error
    """
    name = CharField(max_length=36, help_text="Common name for the property")

    related = CharField(max_length=36, choices=BRANCHES, help_text="Related event or item")
    scope = ForeignKey(Type, blank=True, null=True, related_name='properties', help_text="Type used to filter descendants events. Ex: calling an initiative, get the AssignedContributions amount total", db_constraint=False, on_delete=models.PROTECT)
    attribute = ForeignKey(Attribute, blank=True, null=True, related_name='properties', help_text="Attribute value of the selected scope type action", db_constraint=False, on_delete=models.PROTECT)# (Attribute) # start, end, value, max_bid, min_bid, max_bidding_offers ...
    method = CharField(max_length=36, choices=METHODS, help_text="Method used to get the result")

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

    def get_value(self, mod):
        from ilot.core.models import Moderation
        # if multiple objects, we take the most recent one ?
        if self.method == 'value':

            if self.related == 'this':
                return mod.get_data().get(self.attribute.name)
            elif self.related == 'target':
                return mod.get_target().get_data().get(self.attribute.name)
            elif self.related == 'actor':
                return mod.get_actor().get_data().get(self.attribute.name)
            elif self.related == 'origin':
                return mod.origin.get_data().get(self.attribute.name)
            elif self.related == 'related':
                return mod.related.get_data().get(self.attribute.name)
            else:
                raise

        elif self.method == 'list':
            print('Looking for ', self.scope, ' in ', self.related)
            list = []
            for result in Moderation.objects.filter(related_id=mod.related_id):

                if self.related == 'actor':
                    typed_scope = result.get_actor_infered_types(mod.akey)
                elif self.related == 'target':
                    typed_scope = result.get_actor_infered_types(mod.target)
                else:
                    typed_scope = result.get_infered_types()

                if self.scope and self.scope in typed_scope:
                    list.append( result )

            return list

        elif self.method == 'count':
            counter = 0
            for result in Moderation.objects.filter(related_id=mod.related_id):
                if self.scope:
                    if self.scope in result.get_infered_types():
                        counter+=1
                else:
                    counter+=1
            return counter

        else:
            raise



CONDITIONS = (
    ('equals', 'Equals'),
    ('not-equals', 'Not equals'),
    ('gt', 'Greater than'),
    ('lt', 'Lower than'),
    ('in', 'In'),
    ('not_in', 'not In'),
)



class Condition(AuditedModel):
    """
    Condition is a comparison that returns true or false
    it returns False if either left or right property raises error
    """
    name = CharField(max_length=36, help_text="Common name for the condition")
    parent = ForeignKey('self', blank=True, null=True, related_name='conditions', db_constraint=False, help_text="Parent condition needed to be true", on_delete=models.PROTECT)

    left = ForeignKey(Property, related_name='condition_lefts', db_constraint=False, help_text='Left value', on_delete=models.PROTECT)
    condition = CharField(max_length=36, choices=CONDITIONS, help_text='Condition for the condition')
    right = ForeignKey(Property, related_name='condition_rights', db_constraint=False, blank=True, null=True, help_text='Right value', on_delete=models.PROTECT)

    value = TextField(blank=True, null=True, verbose_name='or ...')

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

    def is_true(self, mod):

        left_value = self.left.get_value(mod)
        if self.right:
            right_value = self.right.get_value(mod)
        else:
            right_value = self.value


        print('Condition ', self.name, mod)

        # None
        if left_value == None: left_value = ''
        if right_value == None: right_value = ''

        # booleans
        if isinstance(left_value, bool):
            if left_value == True: left_value = 1
            else: left_value = 0

        if isinstance(right_value, bool):
            if right_value == True: right_value = 1
            else: right_value = 0

        print('Condition:', left_value, self.condition, right_value)

        if self.condition in 'equals':
            return str(left_value) == str(right_value)

        elif self.condition == 'not-equals':
            return str(left_value) != str(right_value)

        elif self.condition == 'gt':
            try:left_value = int(left_value)
            except:left_value = len(left_value)

            try:right_value = int(right_value)
            except:right_value = len(right_value)

            return left_value > right_value

        elif self.condition == 'lt':
            if right_value == '': right_value = 0
            try:left_value = int(left_value)
            except:pass
            try:right_value = int(right_value)
            except:pass
            return left_value < right_value

        elif self.condition == 'in':
            return left_value in right_value
        elif self.condition == 'not-in':
            return not left_value in right_value
        else:
            return False



BRANCHES =(
    ('target', 'Target'),
    ('actor', 'Actor'),
    ('related', 'Item'),
    ('origin_actor', 'Origin Actor'),
    ('origin_target', 'Origin Target'),
    ('origin_related', 'Origin Item'),
    ('root', 'Root'),
)

class Trigger(AuditedModel):
    """
    A trigger is an automated action triggered
    when the watched status is created (the corresponding action is completed)
    and the provided condition is true,

    then the behavior is dispatched

    with the watched event target as target,
    on behalf of the watched event actor.
    on the same related,
    with the watched event as origin
    """
    name = CharField(max_length=36, default='', help_text="Common name for the trigger")
    #status = ForeignKey(Status, related_name='oldtriggers', verbose_name='----', on_delete=models.PROTECT)
    action = ForeignKey(Action, blank=True, null=True, related_name='triggers', verbose_name='When ...', on_delete=models.PROTECT)
    type = ForeignKey(Type, blank=True, null=True, db_constraint=False,
                      limit_choices_to=Q( Q(reference='event')|Q(reference='related')|Q(reference='context')|Q(reference='actor') ),
                      related_name='triggers', verbose_name='on ', on_delete=models.PROTECT)

    condition = ForeignKey(Condition, blank=True, null=True,
                            related_name='triggers', verbose_name='if',
                            help_text='Condition to be true to do the trigger',
                            db_constraint=False, on_delete=models.PROTECT)

    behavior = ForeignKey(Action, related_name='triggered',
                          help_text='Action to be triggered',
                          db_constraint=False, on_delete=models.PROTECT)

    #actor = CharField(max_length=36, default='actor', choices=BRANCHES, help_text="Behavior actor")
    actor_type = ForeignKey(Type, blank=True, null=True,
                            limit_choices_to=Q( Q(reference='actor')|Q(reference='target')|Q(reference='context') ),
                            related_name='triggers_as_actor',
                            verbose_name='Trigger as ...',
                            db_constraint=False, on_delete=models.PROTECT)

    target_type = ForeignKey(Type, blank=True, null=True,
                             limit_choices_to=Q( Q(reference='actor')|Q(reference='target')|Q(reference='context') ),
                             related_name='triggers_as_target',
                             verbose_name='Trigger to ...',
                             db_constraint=False, on_delete=models.PROTECT)

    order = IntegerField(default=0)

    #target = CharField(max_length=36, default='target', choices=BRANCHES, help_text="Behavior target")

    # data = TextField(default="{}", help_text="Json extra data for the behavior")

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['order', 'name']




REQUIREMENT_REFERENCES = (
    ('event', 'Event'),
    ('actor', 'Actor'),
    ('related', 'Item'),
    ('context', 'Context'),
)

class Requirement(AuditedModel):
    """
    For an action to be processed,
    System checks for requirements to this action
    """
    name = CharField(max_length=36, help_text="Common name for the requirement")
    action = ForeignKey(Action, related_name='requirements',
                        help_text='Action to apply requirements',
                        db_constraint=False, on_delete=models.PROTECT) # to assign

    reference = CharField(max_length=36, default='actor',
                          choices=REQUIREMENT_REFERENCES, verbose_name='')

    condition = ForeignKey(Condition, related_name='requirements',
                           help_text="Condition related",
                           db_constraint=False, on_delete=models.PROTECT) # AssigningAmountIsBudgeted

    message = CharField(max_length=512, help_text="Message for rejected requirement") # Budget is not sufficient to assign this amount
    behavior = ForeignKey(Action, related_name='unfullfilled_requirements',
                          help_text='Maybe Action to fulfill requirement',
                          db_constraint=False, on_delete=models.PROTECT) # budget

    class Meta:
        ordering = ['name']



class RuleManager(Manager):
    item_actor_actions = {}
    item_actor_action_names = {}

class Rule(AuditedModel):
    """

    """
    objects = RuleManager()

    #context
    action = ForeignKey(Action, related_name='rules',
                        verbose_name="doing",
                        db_constraint=False, on_delete=models.PROTECT)

    type = ForeignKey(Type, blank=True, null=True,
                      related_name='rules', verbose_name="on a ",
                      db_constraint=False, on_delete=models.PROTECT)

    is_allowed = BooleanField(default=True)
    actor = ForeignKey(Type, blank=True, null=True,
                     related_name='actors', verbose_name="as a ",
                     db_constraint=False, on_delete=models.PROTECT)

    priority = IntegerField(default=0)
    enabled = BooleanField(default=True)

    def __str__(self):
        return str(self.action)+' on '+str(self.type)

    class Meta:
        ordering = ['actor', 'action']
