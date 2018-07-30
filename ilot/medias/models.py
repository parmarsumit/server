from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

from django.db.models import ImageField
from django.db import models
from ilot.core.models import AuditedModel

from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location='/srv/media')

from ilot.core.models import request_switch

import os
import hashlib

def upload_to(instance, filename):
    """
    Path and filename to upload to
    """
    #print('uploading to '+instance.get_path()+'.'+filename)
    #return instance.get_path()+'.'+filename
    filename, ext = os.path.splitext(filename)

    folder = hashlib.md5(request_switch.interface.id.encode('utf-8')).hexdigest()
    filename = hashlib.md5((instance.id).encode('utf-8')).hexdigest()
    return folder+'/'+filename+ext.lower()


class Media(AuditedModel):

    actor = models.CharField(max_length=36)
    item = models.CharField(max_length=36)

    image = models.ImageField(upload_to=upload_to, blank=True, null=True)

    avatar = ImageSpecField(source='image',
                            processors=[ResizeToFill(100, 100)],
                            format='PNG',
                            options={'quality': 60})

    thumbnail = ImageSpecField(source='image',
                            processors=[ResizeToFit(256, 256)],
                            format='PNG',
                            options={'quality': 60})

    #
    file = models.FileField(upload_to=upload_to, blank=True, null=True)
