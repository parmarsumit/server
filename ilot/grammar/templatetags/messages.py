
from ilot.core.models import request_switch
from ilot.grammar.models import Panel, Message, parse_message
from ilot.rules.models import Status
from django.utils.html import format_html
from django import template
register = template.Library()

import traceback

@register.simple_tag(takes_context=False)
def get_context_message(mod):

    try:
        from ilot.meta.models import ActorNotification
        anotif = ActorNotification.objects.filter(event_id=mod.id, context__actor_id=request_switch.akey)[0]
        return anotif.get_notif_message()
    except IndexError:
        from ilot.grammar.models import Notification
        try:
            notif = Notification.objects.filter(type__in=mod.origin.get_infered_types(),
                                                status__name=mod.status)
            #print('GOT MESSAGES', notif.count(), notif[0], notif[0].for_actor)
            return notif[0].get_parsed_message(mod)
        except IndexError:
            return Notification().get_parsed_message(mod)


@register.simple_tag(takes_context=False)
def get_context_action(mod, action, label):

    if not action:
        return 'missing action'

    from ilot.rules.models import Action
    action_item = Action.objects.get(name=action).get_panel()

    if label == 'success':
        action_message = action_item.get_acting_success(mod)
    elif label == 'label':
        action_message = action_item.get_acting_label(mod)
    elif label == 'title':
        action_message = action_item.get_acting_title(mod)
    elif label == 'confirm':
        action_message = action_item.get_acting_confirm(mod)
    elif label == 'help':
        action_message = action_item.get_acting_help(mod)
    else:
        action_message = 'unknown'

    return action_message
