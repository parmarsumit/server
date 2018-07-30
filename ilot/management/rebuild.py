

from ilot.core.models import InferedType, Moderation
InferedType.objects.all().delete()
for mod in Moderation.objects.all().order_by('ref_time'):
    mod.save_infered_types()
