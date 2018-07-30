from django import forms
from django.contrib import admin
from django.forms.models import ModelForm
from ilot.cloud.models import Service, Container, Process, Frontend

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_date', 'container', 'interface', 'modified_date']
admin.site.register(Service, ServiceAdmin)

class ContainerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_date', 'name', 'ip', 'capacity', 'modified_date', 'enabled']
    list_filter = ['enabled']
admin.site.register(Container, ContainerAdmin)

class ProcessAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_date', 'container', 'port', 'status', 'modified_date', 'enabled']
    list_filter = ['enabled', 'status']
admin.site.register(Process, ProcessAdmin)

class FrontendAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_date', 'container', 'ip', 'port', 'modified_date']
admin.site.register(Frontend, FrontendAdmin)
