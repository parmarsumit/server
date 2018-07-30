from django import forms
from django.contrib import admin
from ilot.data.models import DataBlock

class DataBlockAdmin(admin.ModelAdmin):
    list_display = ('related', 'origin', 'name', 'value', 'created_date')
    search_fields = ('value',)
admin.site.register(DataBlock, DataBlockAdmin)
