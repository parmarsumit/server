from django import forms
from django.contrib import admin
from django.forms.models import ModelForm

from ilot.meta.models import ActorInferedType, ActorNotification


class ActorInferedTypeAdmin(admin.ModelAdmin):
    model = ActorInferedType
    list_filter = ['type',]
    list_display = ('context', 'actor', 'type', 'created_date', 'modified_date', )
    ordering = ('-modified_date',)
admin.site.register(ActorInferedType, ActorInferedTypeAdmin)


class ActorNotificationAdmin(admin.ModelAdmin):
    model = ActorNotification
    list_display = ('context', 'rule', 'request', 'created_date', 'modified_date', )
    ordering = ('-modified_date',)
admin.site.register(ActorNotification, ActorNotificationAdmin)
