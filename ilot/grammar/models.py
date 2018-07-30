from ilot.core.models import AuditedModel, Item, DataPath
from ilot.core.models import request_switch, Translation, Moderation
from django.db.models.fields import CharField, BooleanField, EmailField, IntegerField, TextField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db import models
from django.db.models.query_utils import Q
from django.utils.html import format_html

from django.template.base import Template
from django.template.context import Context

META_TYPES = (
    ('item', 'Item'),
    ('version', 'Version'),
    ('event', 'Event'),
    ('request', 'Request')
)

def parse_message(text, node, target=None, links=True, action=None):
    if not target:
        target = node.get_target()
    if '{{' in text or '{%' in text:
        template_args = {
            'origin': node,
            'target':target,
            'action': action,
            'links': links
        }
        context = Context(template_args)
        parsed_message = Template(text).render(context)
        return format_html(parsed_message)

    fallback = None
    vars = {}
    if not action:
        vars['ACTION'] = node.action
    else:
        vars['ACTION'] = action
    vars['ACTOR'] = node.get_actor()
    vars['ORIGIN'] = node.origin
    vars['TARGET'] = target
    vars['PARENT'] = node.related.parent
    vars['ROOT'] = node.related.get_root()
    vars['ITEM'] = node.related
    vars['STATUS'] = node.status

    for keyword in vars.keys():

        if vars[keyword].__class__ in (Item, Translation, Moderation):
            title = vars[keyword].related.get_data().get('title', '------')
            url = vars[keyword].get_url()
            if links:
                replacement = '<a class="text-primary subpanel" href="'+url+'" >'+title+'</a>'
            else:
                replacement = title
        else:
            if links:
                replacement = '<a class="subpanel" href="'+node.get_url()+'index/" >'+str(vars[keyword])+'</a>'
            else:
                replacement = str(vars[keyword])

        text = text.replace(keyword, replacement)

    return format_html(text)




class Panel(AuditedModel):
    action = ForeignKey('rules.Action', related_name='panels', blank=True, null=True, on_delete=models.PROTECT)
    description = CharField(max_length=4096, default='', blank=True, null=True)

    i_label = CharField("Short Button label",
                        max_length=4096,
                        default='ACTION',
                        help_text="""Action button main label <br/>
ex: Create project ...""")

    i_confirmation = CharField("Confirmation Button label",
                        max_length=4096,
                        default="Lets'do ACTION !",
                        help_text="""Action button long label, like a conclusion <br/>
ex: Start your new project""")

    i_title = CharField("Side panel title",
                        max_length=4096,
                        default='ACTION on ORIGIN',
                        help_text="""Action form title <br/>
ex: Create you project !""")

    i_dialog = CharField("Dialog title",
                        max_length=4096,
                        default='ACTION on ORIGIN',
                        help_text="""Action dialog title <br/>
ex: Create you project !""")

    i_help = TextField("Help Text", default='', blank=True,
                       help_text="""Long help text for the action""")

    i_success = CharField("Success message", max_length=4096,
                          default='You did ACTION on ITEM',
                          help_text="""Confirmation message <br/>
ex: Your invitation to TARGET has been sent !
""")

    dialog = BooleanField(default=False, verbose_name="Action is a dialog")
    confirm = BooleanField(default=False, verbose_name="Ask for user confirm on direct submit")
    close = BooleanField(default=True, verbose_name="Close on success")
    redirect = ForeignKey('rules.Action',
                          limit_choices_to=Q(meta_type='request'),
                          default=None, blank=True, null=True,
                          verbose_name="Action to redirect on success")

    def __str__(self):
        return str(self.action)

    def get_acting_label(self, mod):
        return parse_message(self.i_label, mod, links=False, action=self.action.name)

    def get_acting_title(self, mod):
        return parse_message(self.i_title, mod, action=self.action.name)
        if request_switch.akey == mod.akey:
            return parse_message(self.i_title, mod, action=self.action.name)
        else:
            return parse_message(self.other_title, mod, action=self.action.name)

    def get_acting_confirm(self, mod):
        return parse_message(self.i_confirmation, mod, links=False, action=self.action.name)

    def get_acting_dialog(self, mod):
        return parse_message(self.i_dialog, mod, action=self.action.name)

    def get_acting_help(self, mod):
        return parse_message(self.i_help, mod, action=self.action.name)

    def get_acting_success(self, mod):
        return parse_message(self.i_success, mod, action=self.action.name)
        if request_switch.akey == mod.akey:
            return parse_message(self.i_success, mod, action=self.action.name)
        else:
            return parse_message(self.other_success, mod, action=self.action.name)


class Message(AuditedModel):
    """
    Sentence that appears in feeds
    """
    type = ForeignKey('rules.Type', related_name='messages', blank=True, null=True, verbose_name='on a', on_delete=models.PROTECT)
    status = ForeignKey('rules.Status', related_name='messages', verbose_name='When', on_delete=models.PROTECT)

    i_did = CharField(max_length=4096, default='You did STATUS on ITEM', blank=True, null=True)
    target_did = CharField(max_length=4096, default='ACTOR did STATUS on ITEM', blank=True, null=True)
    others_did = CharField(max_length=4096, default='ACTOR did STATUS on ITEM', blank=True, null=True)

    def __str__(self):
        return str(self.type)+'/'+str(self.status)


class Notification(AuditedModel):
    """
    Rules for notifications
    """
    type = ForeignKey('rules.Type', related_name='notifications',
                        blank=True, null=True, verbose_name='on a',
                        db_constraint=False, on_delete=models.PROTECT)
    status = ForeignKey('rules.Status', related_name='notifications',
                        verbose_name='When',
                        db_constraint=False, on_delete=models.PROTECT)
    target = ForeignKey('rules.Type', related_name='notification_targets',
                        blank=True, null=True, verbose_name='tell',
                        db_constraint=False, on_delete=models.PROTECT)

    todo = BooleanField(default=False, verbose_name="Is Todo")
    silent = BooleanField(default=False, verbose_name="Is silent")

    discards = ForeignKey('self', related_name='discarding',
                          verbose_name='Discards ...',
                          blank=True, null=True,
                          db_constraint=False, on_delete=models.PROTECT)
    #
    condition = ForeignKey('rules.Condition', blank=True, null=True, related_name='notifications', help_text='Condition to be true to notify by email', on_delete=models.PROTECT)

    #
    for_target = CharField(max_length=4096, verbose_name='Notification', default='You did STATUS on ITEM', blank=True, null=True)
    webhook = ForeignKey('webhooks.Webhook', related_name='notifications',
                         blank=True, null=True, verbose_name='Webhook',
                         db_constraint=False, on_delete=models.PROTECT)
    title = CharField(max_length=156, verbose_name='Webhook title', default='', blank=True)
    message = TextField(verbose_name='Webhook message', blank=True, null=True)

    #
    for_others = CharField(max_length=4096, verbose_name='Event observed', default='ACTOR did STATUS on ITEM', blank=True, null=True)

    #
    for_actor = CharField(max_length=4096, verbose_name='Event actor - deprecated', default='You did STATUS on ITEM', blank=True, null=True)


    class Meta:
        ordering = ['type', 'status', 'target']

    def __str__(self):
        return str(self.type)+'/'+str(self.status)+'>'+str(self.target)

    def get_parsed_message(self, event, actor=None):
        #return parse_message(self.for_others, event)
        if not actor:
            actor = request_switch.akey
        #if event.akey == actor:
        #    message = parse_message(self.for_actor, event)
        if event.target == actor:
            message = parse_message(self.for_target, event)
        else:
            message = parse_message(self.for_others, event)
        return message
