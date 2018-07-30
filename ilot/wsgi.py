# -*- coding: utf-8 -*-
"""
WSGI config for ilot.
"""
import os

os.environ.setdefault("DJANGO_ENV", "production")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ilot.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
