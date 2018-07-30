'''
Created on 15 janv. 2013

@author: rux
'''
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm

from ilot.core import models
from ilot.core.models import Item, Translation, Moderation


def current_url(obj):
    return obj.get_url()

def current_label(obj):
    return obj.get_data().get('label')

def current_slug(obj):
    return obj.get_data().get('slug')

def current_title(obj):
    return obj.get_data().get('title')


class DataPathAdmin(admin.ModelAdmin):
    model = models.DataPath
    list_filter = ['action',]
    list_display = ('akey', 'version', 'context', 'action', 'data', 'ref_time', 'visible', 'created_date', 'modified_date', )
    ordering = ('-ref_time',)
admin.site.register(models.DataPath, DataPathAdmin)


class ModerationAdmin(admin.ModelAdmin):
    list_filter = ['status',]
    list_display = ('ref_time', 'version', 'context', 'action', 'status', 'type', 'related', 'origin', 'target', 'data')
    ordering = ('-ref_time',)
    readonly_fields = ('related', 'origin')

admin.site.register(Moderation, ModerationAdmin)


def key_slug(obj):
    return obj.related.slug

class ItemForm(ModelForm):
    class Meta:
        model = Item
        exclude = ('created_by', 'modified_by', )

class TranslationForm(ModelForm):
    class Meta:
        model = Translation
        exclude = ('created_by', 'modified_by', )


#class TranslationInline(admin.StackedInline):
#    model = models.Translation
#    extra = 1
#    min_num = 1

class ItemAdmin(admin.ModelAdmin):

    form = ItemForm
    list_display = ['parent', 'type', 'action', 'status', 'ref_time']

    #list_display_links = ['title', 'slug', 'label']
    #actions = ['mark_published', 'mark_not_published']

    #inlines = [TranslationInline]

    #list_editable = ('published', )
    sortable = 'order'
    mptt_level_indent = 20

    search_fields = ('id',
                     'content', 'data')

    #date_hierarchy = 'created_date'
    #list_filter = [ 'published', ]

    raw_id_fields = ('related', 'parent', 'origin')
    readonly_fields = ('related', 'parent', 'origin')

    def mark_published(self, request, queryset):
        rows_updated = 0
        for item in queryset.iterator():
            if not item.published:
                item.published = True
                item.save()
                rows_updated += 1

        if rows_updated == 1:
            message = _(u"1 item was published.")
        else:
            message = _(u"%s items were published.") % rows_updated
        self.message_user(request, message)

    def mark_not_published(self, request, queryset):
        rows_updated = 0
        for item in queryset.iterator():
            if item.published:
                item.published = False
                item.save()
                rows_updated += 1

        if rows_updated == 1:
            message = _(u"1 item was marked as not published.")
        else:
            message = _(u"%s items were marked as not published.") % rows_updated
        self.message_user(request, message)

admin.site.register(models.Item, ItemAdmin)



def model_link(obj):
    try:
        url = reverse('admin:content_item_change', args=(obj.related.pk,))
        return '<a href="%s">>> Item</a>' % url
    except:
        return ''

model_link.allow_tags = True


def public_link(obj):
    url = obj.get_url()
    return '<a href="%s" target="_blank" >>> Open</a>' % url

public_link.allow_tags = True

def redirect_link(obj):
    if obj.url:
        url = obj.url
        return '<a href="%s" target="_blank" >>> Trans Redirect</a>' % url
    elif obj.related.url:
        url = obj.related.url
        return '<a href="%s" target="_blank" >>> Item Redirect</a>' % url
    else:
        url = obj.get_url()
        return '<a href="%s" target="_blank" >>> Page</a>' % url

redirect_link.allow_tags = True



class TranslationAdmin(admin.ModelAdmin):
    form = TranslationForm
    list_display = ['ref_time', 'related', 'locale', 'action', 'status', current_url, current_title, public_link]
    list_display_links = [current_url, current_title]
    #search_fields = ['slug', 'label', 'title', 'description']
    ordering = ['-ref_time', '-modified_date']

admin.site.register(models.Translation, TranslationAdmin)
