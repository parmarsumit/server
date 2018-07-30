'''
Created on Feb 10, 2015

@author: nicolas
'''
import os

from django import template

from ilot.core.models import DataPath, Moderation
from ilot.core.manager import AppManager
from ilot.models import has_perm

from django.db.models import ObjectDoesNotExist

from django import template
register = template.Library()


from ilot.core.manager import AppManager
from django.core.exceptions import PermissionDenied
from django.http.response import Http404

from django import template
register = template.Library()

def getAttr(value, arg):
    if value:
        return value.__getattribute__(arg)
    else:
        return ""

register.filter('getAttr', getAttr)

@register.simple_tag(takes_context=False)
def raise_403():
    raise PermissionDenied


class FormatTimeNode(template.Node):
    def __init__(self, date_to_be_formatted, format_string):
        self.date_to_be_formatted = template.Variable(date_to_be_formatted)
        self.format_string = format_string

    def render(self, context):
        try:
            actual_date = self.date_to_be_formatted.resolve(context)
            return actual_date.strftime(self.format_string)
        except template.VariableDoesNotExist:
            return ''

register.tag('current_time', FormatTimeNode)

from ilot.core.parsers.api_json import dump_json
def jsonify(object):
    #if isinstance(object, QuerySet):
    #    return serialize('json', object)
    return dump_json(object)

register.filter('jsonify', jsonify)
