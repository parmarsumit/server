from django import forms
from django.contrib import admin
from django.forms.models import ModelForm
from ilot.grammar.models import Panel, Message, Notification


class PanelAdmin(admin.ModelAdmin):
    #list_filter = ['model', 'target', 'behavior']
    list_display = ('action', 'description', 'close', 'redirect', 'i_label', 'i_title')
    #read_only = ('status',)
    #exclude = ('model', 'target', 'behavior', 'create', 'other_title', 'other_success')
admin.site.register(Panel, PanelAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_editable = ['discards', 'todo', 'webhook']
    list_display = ('type', 'status', 'target', 'todo', 'discards', 'webhook')
admin.site.register(Notification, NotificationAdmin)
