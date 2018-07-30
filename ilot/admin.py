from django import forms
from django.contrib import admin
from django.forms.models import ModelForm
from ilot.models import Organization, Release, Package, Authorization, Interface

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'enabled')
admin.site.register(Organization, OrganizationAdmin)


class InterfaceForm(forms.ModelForm):
    class Meta:
        model = Interface
        exclude = tuple()
    def __init__(self, *args, **kwargs):
        super(InterfaceForm, self).__init__(*args, **kwargs)

class InterfaceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'cname', 'application')
    form = InterfaceForm
admin.site.register(Interface, InterfaceAdmin)

class PackageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'created_date')
admin.site.register(Package, PackageAdmin)

class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'created_date')
admin.site.register(Release, ReleaseAdmin)

class AuthorizationAdmin(admin.ModelAdmin):
    #raw_id_fields = ('profile',)
    list_display = ('__str__', 'organization', 'akey', 'action', 'origin', 'enabled', 'created_date')
admin.site.register(Authorization, AuthorizationAdmin)
