'''
Created on 17 mars 2015

@author: rux
'''
import json

import django
from django.db.models.fields.files import ImageFieldFile, FieldFile
from collections import OrderedDict
import traceback

def API_json_parser(obj):
    """Default JSON serializer."""
    import calendar
    import datetime

    if isinstance(obj, datetime.date):
        return str(obj)

    elif isinstance(obj, datetime.datetime):
        # TODO
        # set iso 8601
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return millis

    elif isinstance(obj, ImageFieldFile):
        # create a json object
        return {'name':obj.name, 'path':obj.path, 'url':obj.url}
        return obj.name
    elif isinstance(obj, FieldFile):
        return {'name':obj.name, 'path':obj.path, 'url':obj.url}
        return obj.name
    #elif isinstance(obj, decimal.Decimal):
    #    return str(obj)
    #elif isinstance(obj, ModelField):
    #    return str(obj.value())

    try:
        return str(obj)
    except:
        raise TypeError("Unserializable object %s of type %s" % (obj, type(obj)
                                                                 ))


def API_json_loader(obj):
    """Default JSON deserializer."""
    return obj

def load_json(value):
    """
    Unserialize json string
    """
    try:
        return json.loads(value)
    except:
        print('ERROR LOADING JSON')
        print(type(value))
        print(repr(value))
        print(value)
        traceback.print_exc()
        raise

def dump_json(value):
    """
    Serialize json string
    """
    if isinstance(value, str):
        return value

    if not isinstance(value, (list, dict, OrderedDict)):
        print(type(value))
        print(repr(value))
        print(value)
        raise

    return json.dumps(value, default=API_json_parser, sort_keys=False)
