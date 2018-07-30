from ilot.core.models import AuditedModel, Item

from django.db import models


class DataBlock(AuditedModel):
    related = models.CharField(max_length=36, null=False, blank=True)
    origin = models.CharField(max_length=36)
    attribute = models.CharField(max_length=36)
    name = models.CharField(max_length=36)
    value = models.TextField(null=False, blank=True)

    replaced = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(DataBlock, self).save(*args, **kwargs)
        if self.origin in Item.objects.tree_id_data:
            del Item.objects.tree_id_data[self.origin]
        if self.related and self.related in Item.objects.tree_id_data:
            del Item.objects.tree_id_data[self.related]
            #related = Item.objects.get_at_id(self.related)
            #related._data = None
