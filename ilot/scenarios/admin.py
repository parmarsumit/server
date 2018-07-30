from django import forms
from django.contrib import admin
from ilot.scenarios.models import Scenario, Step, Avatar

class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_date')
admin.site.register(Scenario, ScenarioAdmin)

class AvatarAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_date')
admin.site.register(Avatar, AvatarAdmin)

class StepAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_date')
admin.site.register(Step, StepAdmin)
