from django.core.exceptions import SuspiciousFileOperation
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join

from django.template.loaders.base import Loader as BaseLoader

from ilot.core.models import request_switch
from django.conf import settings
import os
import io
"""
Wrapper for loading templates for the domain.
"""

class Loader(BaseLoader):
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):

        from ilot.cloud.models import Service
        try:
            app = Service.objects.get(interface=request_switch.interface)
            template_dir = os.path.join(app.path, 'templates/')
        except Service.DoesNotExist:
            from django.conf import settings
            template_dir = os.path.join(settings.APP_ROOT, 'templates/')
        #print('TEMPLATE DIR', template_dir, request_switch.interface)
        try:
            yield safe_join(template_dir, template_name)
        except SuspiciousFileOperation:
            # The joined path was located outside of this template_dir
            # (it might be inside another one, so this isn't fatal).
            pass

        #if hasattr(request_switch, 'application'):
        #    template_dir = settings.CONTAINERS_ROOT+'/repository/'+request_switch.project.repository+'/templates'


    def load_template_source(self, template_name, template_dirs=None):
        tried = []
        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                with io.open(filepath, encoding=self.engine.file_charset) as fp:
                    return fp.read(), filepath
            except IOError:
                tried.append(filepath)
        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = ("Your template directories configuration is empty. "
                         "Change it to point to at least one template directory.")
        raise TemplateDoesNotExist(error_msg)

    load_template_source.is_usable = True
