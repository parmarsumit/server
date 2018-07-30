from django import forms
from django.contrib import admin
from django.forms.models import ModelForm
from ilot.rules.models import Action, Status, Rule, Attribute, Type, Property, \
                              Condition, Requirement, Trigger


class StatusModelChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return obj.name
         if obj.past:
             return obj.past
         else:
             return '*'+obj.name
         return "%s" % (obj.description)

class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'shared', 'description')
admin.site.register(Status, StatusAdmin)


class ActionModelChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         if obj.present:
             return obj.present
         else:
             return '*'+obj.name

class RuleAdmin(admin.ModelAdmin):
    list_filter = ['action', 'type',]
    list_editable = ['actor']
    list_display = ('type', 'action', 'is_allowed', 'actor', 'enabled')
admin.site.register(Rule, RuleAdmin)


class RuleInline(admin.StackedInline):
    model = Rule
    fk_name = 'action'
    extra = 0
    show_change_link = True
    fields = ('action', 'type', 'is_allowed', 'actor')

class AttributeInline(admin.StackedInline):
    model = Attribute
    fk_name = 'action'
    extra = 0
    show_change_link = True
    fields = ('name', 'label', 'datatype', 'default')
    #readonly_fields = ('name', 'label', 'datatype', 'default')

class ActionAdmin(admin.ModelAdmin):
    list_editable = ['package']
    list_filter = ['package', 'target_type']
    list_display = ( 'name', 'meta_type', 'status', 'target_type', 'behavior', 'description', 'package',)
    #read_only = ('status',)
    #exclude = ('model', 'target', 'behavior', 'create', 'other_title', 'other_success')
    inlines = [
        AttributeInline,
        RuleInline,
    ]
admin.site.register(Action, ActionAdmin)


class AttributeAdmin(admin.ModelAdmin):
    list_filter = ['action', 'name']
    list_display = ('name', 'action', 'label', 'datatype')
admin.site.register(Attribute, AttributeAdmin)


class TypeAdminForm(forms.ModelForm):
    #status = StatusModelChoiceField(label='A', queryset=Status.objects.all())
    class Meta:
          model = Type
          exclude = tuple()

class RuleTypeInline(admin.StackedInline):
    model = Rule
    fk_name = 'type'
    extra = 0
    show_change_link = True
    fields = ('action', 'type', 'is_allowed', 'actor')

class TypeAdmin(admin.ModelAdmin):
    form = TypeAdminForm
    list_display_links = ('name',)
    list_editable = ['package']
    list_filter = ['overrides', 'package', 'type', 'status', 'reference']
    list_display = ('name', 'type', 'status', 'overrides', 'reference','package')
    inlines = [
        RuleTypeInline,
    ]
admin.site.register(Type, TypeAdmin)

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'related', 'scope', 'attribute', 'method')
admin.site.register(Property, PropertyAdmin)

class ConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'left', 'condition', 'right')
admin.site.register(Condition, ConditionAdmin)

class TriggerAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'action', 'condition', 'behavior')
admin.site.register(Trigger, TriggerAdmin)

class RequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'action', 'condition', 'message', 'behavior')
admin.site.register(Requirement, RequirementAdmin)
