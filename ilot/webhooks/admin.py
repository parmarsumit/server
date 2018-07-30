from django import forms
from django.contrib import admin
from django.forms.models import ModelForm
from ilot.webhooks.models import Webhook, WebhookRequest


class WebhookAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
admin.site.register(Webhook, WebhookAdmin)

class WebhookRequestAdmin(admin.ModelAdmin):
    list_display = ('url', 'done', 'response_code', 'created_date')
admin.site.register(WebhookRequest, WebhookRequestAdmin)
