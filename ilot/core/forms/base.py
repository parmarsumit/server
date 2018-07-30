'''
Created on 2 fevr. 2015

@author: nicolas
'''
from django.forms.models import ModelForm
from django.forms.forms import Form
from django.forms.fields import CharField
from ilot.rules.models import Action, Attribute
from ilot.core.models import Item, Moderation, Translation, DataPath

from django.forms.fields import CharField, BooleanField, IntegerField, \
                                FloatField, EmailField, SlugField, URLField, \
                                ImageField, FileField

from django.forms import Textarea

from django.forms import ModelChoiceField
from ilot.core.manager import AppManager
from django.db.models import ObjectDoesNotExist
from ilot.data.models import DataBlock
from django.db.models.query_utils import Q
from django.core.validators import RegexValidator
from django import forms

class FormControlMixin(object):
    def set_form_control_class(self):
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

class BaseModelForm(FormControlMixin, ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)
        self.set_form_control_class()


def get_targets(instance, ntype):

    suffix = 'items'
    if ntype.reference == 'actor':
        suffix = 'actors'
    elif ntype.reference == 'target':
        suffix = 'targets'

    if ntype.scope == 'children':
        typed = instance.related.parent.do_query('query_children_'+ntype.name)
    elif ntype.scope == 'descendants':
        typed = instance.related.get_root().do_query('query_descendants_'+ntype.name)
    else:
        if ntype.reference == 'context':
            typed = instance.do_query('query_all_'+ntype.name)
        else:
            typed = instance.do_query('query_this_'+ntype.name)

    return typed

class BaseActionForm(BaseModelForm):
    """
    Base action pipe model form
    """
    is_saved = False
    action_item = None
    model_fields = ['label', 'title', 'description', 'slug']
    __authorize__ = False

    class Meta:
        model = Item
        fields = []

    def __init__(self, action, *args, **kwargs):

        # build the forms from the action attributes
        try:
            self.action_item = Action.objects.get(name=action)
        except ObjectDoesNotExist:
            self.action_item = Action(name=action,)

        attributes = self.action_item.attributes.all()

        from django.forms.models import fields_for_model
        model_fields = fields_for_model(Translation)

        model_fields = {}

        #for field in model_fields_list:
        #    print(field)
        #    model_fields[ field ] = model_fields_list[field]

        #for attr in attributes:
        #    if attr.datatype in model_fields:
        #        self.Meta.fields.append(attr.datatype)

        #if self.action_item.target_type:
        #    if not 'target' in self.Meta.fields:
        #        self.Meta.fields.append('target')

        super(BaseActionForm, self).__init__(*args, **kwargs)

        # build fields from attributes
        attributes = self.action_item.attributes.all()

        for attr in attributes:

            if attr.datatype == 'target':
                qs = Item.objects.filter(id__in=list(get_targets(self.instance, self.action_item.target_type)))
                att_field = TargetModelChoiceField(queryset=qs, )

            elif attr.datatype == 'query':
                qs = Item.objects.filter(id__in=list(get_targets(self.instance, self.action_item.target_type)))
                att_field = TargetQueryField(queryset=qs, initial=None)

            elif attr.datatype == 'string':
                att_field = CharField(max_length=1024)

            elif attr.datatype == 'markdown':
                att_field = CharField(max_length=25600, widget=Textarea)

            elif attr.datatype == 'description':
                att_field = CharField(max_length=25600000, widget=Textarea)

            elif attr.datatype == 'boolean':
                att_field = BooleanField()

            elif attr.datatype == 'integer':
                att_field = IntegerField()

            elif attr.datatype == 'number':
                att_field = FloatField()

            elif attr.datatype == 'email':
                att_field = EmailField()

            elif attr.datatype == 'slug':
                att_field = SlugField()

            elif attr.datatype == 'url':
                att_field = URLField()

            #elif attr.datatype in model_fields:
            #    att_field = model_fields[ attr.datatype ]

            elif attr.datatype == 'image':
                att_field = MediaUploadField()

            else:
                #continue
                att_field = CharField(max_length=1024)

            att_field.initial = attr.default
            att_field.required = attr.required
            att_field.label = attr.label
            att_field.help_text = attr.help

            self.fields[attr.name] = att_field

            if attr.hidden:
                self.fields[attr.name].widget = forms.HiddenInput()

            if attr.regexp:
                validator = RegexValidator(attr.regexp,
                                            message=attr.regexp_error)
                if not att_field.validators:
                    att_field.validators = []
                att_field.validators.append(validator)

        self.set_form_control_class()

    def clean(self, *args, **kwargs):
        #print('FULL CLEAN FORM', args, kwargs)
        #if self.action_item.meta_type != 'request':
        #    self.instance.status = self.action_item.status.name

        #if self.is_bound:
        attributes = self.action_item.attributes

        for attr in attributes.all():
            value = self.get_field_value(attr.name)

            if attr.datatype == 'query':
                # check if we can query the value
                value = self.fields[attr.name].find_one(value)
                if attr.name == 'target':
                    self.instance.target = value

            if attr.unique and value:
                if value != self.instance.get_data().get(attr.name):
                    # test it exists only for the node scope
                    if DataBlock.objects.filter(name=attr.name,
                                                value=value,
                                                replaced=False).exclude(related=self.instance.related_id).values_list('related', flat=True).count():

                        # it's bound to another node
                        # we raise validation error
                        error_msg = str(value)+' is already taken !'
                        raise forms.ValidationError(error_msg)

        return super(BaseActionForm, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):

        if self.action_item.authorize and not self.__authorize__:
            """
            Authorization is required to finish the request
            """
            raise PermissionDenied

        #if self.action_item.meta_type != 'request':
        #    self.instance.status = self.action_item.status.name

        if self.action_item.meta_type != 'request':
            # collect form fields as data dict
            form_data = self.get_data()
            attributes = self.action_item.attributes.all()

            #
            if self.action_item.meta_type == 'clone':
                attributes_ids = attributes.values_list('id', flat=True)
                datablocks = {}
                for datablock in DataBlock.objects.filter(origin=self.instance.origin.id).order_by('ref_time'):
                    if not datablock.attribute in attributes_ids:
                        datablocks[datablock.attribute] = (datablock.name, datablock.value)
                for key in datablocks:
                    DataBlock(related=self.instance.related_id,
                              origin=self.instance.id,
                              attribute=key,
                              name=datablocks[key][0],
                              value=datablocks[key][1]).save()

            for attr in attributes:

                if self.action_item.meta_type == 'version':
                    # markup replaced fields as disabled
                    DataBlock.objects.filter(related=self.instance.related_id,
                                             name=attr.name).update(replaced=True)

                if attr.datatype == 'query':
                    # check if we can query the value
                    form_data[attr.name] = self.fields[attr.name].find_one(form_data[attr.name])
                    # print('Setting queried name to ', form_data[attr.name])

                if attr.datatype == 'image':

                    print('IMAGE', form_data[attr.name])

                    media = self.fields[attr.name].save_media(form_data[attr.name], self.instance)
                    if media:
                        form_data[attr.name] = self.fields[attr.name].media.id
                        print('SAVED IMAGE', form_data[attr.name])
                    else:
                        form_data[attr.name] = self.instance.get_data().get(attr.name, '')
                        print('KEEPING', self.fields[attr.name], form_data[attr.name])

                if attr.name == 'target':
                    if not form_data[attr.name]:
                        if not self.instance.target:
                            self.instance.target = self.instance.akey
                        continue
                    else:
                        self.instance.target = form_data[attr.name]

                if attr.name == 'parent':
                    self.instance.parent_id = form_data[attr.name]

                DataBlock(related=self.instance.related_id,
                          origin=self.instance.id,
                          attribute=attr.id,
                          name=attr.name,
                          value=form_data[attr.name]).save()

            new_dat = self.instance.get_data(refresh=True)
            #new_dat.update(form_data)
            #print(new_dat)

            Item.objects.tree_id_data[self.instance.id] = self.instance._data = new_dat

        # instance_data = self.instance.get_data()
        # instance_data.update(form_data)
        # self.instance.set_data(instance_data)

        return super(BaseActionForm, self).save(*args, **kwargs)

    def get_field_value(self, field_name):
        value = self[field_name].value()

        if value is None:
            try:
                value = self._raw_value(field_name)
            except:
                pass

        return value

    def get_data(self):
        """
        Get the form fields data as dict
        """
        from ilot.core.parsers.api_json import API_json_parser
        data = {}
        for field_name in self.fields:
            data[field_name] = self.get_field_value(field_name)
            if data[field_name] is None:
                data[field_name] = ''
        return data


import os
import hashlib

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


class MediaUploadField(ImageField):

    media = None

    def save_media(self, data, instance):
        """
        Save the file to media item ?
        """
        from ilot.medias.models import Media
        ufile = self.to_python(data)
        if ufile:
            media = Media(actor=instance.akey, item=instance.related_id, image=ufile)
            media.save()
            self.media = media
            return media
        else:
            return None

    def get_media_url(self):
        return self.media.id

class TargetModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_display()

class TargetQueryField(CharField):
    _qs = None

    def __init__(self, queryset, *args, **kwargs):
        super(TargetQueryField, self).__init__(*args, **kwargs)
        self._qs = queryset

    def clean(self, value):
        if not value:
            raise forms.ValidationError('Requires value')
        return self.find_one(value)

    def find_one(self, value):
        query_able_field = ('username', 'email')
        print('Find one in ', self._qs.filter(id='10e11772-1258-4364-a244-3e4f05403b2e') )
        data_blocks = DataBlock.objects.filter(value=value,
                                               name__in=query_able_field,
                                               related__in=self._qs.values_list('related_id', flat=True).distinct(),
                                               replaced=False,
                                               ).order_by('-ref_time')
        if data_blocks.count():
            # verify it's the same user
            relateds = data_blocks.values_list('related', flat=True).distinct()
            if relateds.count() > 1:
                raise forms.ValidationError('Too many results')
            else:
                return data_blocks[0].related
                from ilot.core.models import Moderation
                mod = Moderation.objects.get(id=data_blocks[0].related)
                print('TARGET', mod.get_data(), mod.related.get_display())
                return mod.related_id
        else:
            raise forms.ValidationError('No results.')

    #def label_from_instance(self, obj):
    #    return obj.get_display()
