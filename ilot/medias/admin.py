from ilot.medias.models import Media
from django.contrib import admin

class MediasAdmin(admin.ModelAdmin):
    list_display = ('item', 'actor', 'image', 'file')
admin.site.register(Media, MediasAdmin)
