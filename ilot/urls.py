from django.conf import settings
#from django.conf.urls import *  # NOQA
#from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
import os
from ilot.views.front import FrontView
from ilot.views.site import SiteView
from ilot.rules.models import Type

admin.autodiscover()

from ilot.core.manager import AppManager
from django.conf.urls import include, url

handler401 = 'ilot.views.front.handler401'
handler404 = 'ilot.views.front.handler404'
handler403 = 'ilot.views.front.handler403'
handler500 = 'ilot.views.front.handler500'

# comming soon
import re
re_uuid = re.compile("[0-F]{8}-[0-F]{4}-[0-F]{4}-[0-F]{4}-[0-F]{12}", re.I)

# https://gist.github.com/luzfcb/186ee28b368450035e056228615db999
# okey this may be interesting to handle uppercase or lowercase
#
uuid_slug_regexp = '(?P<path>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})'

AppManager.register_section(FrontView)

from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [

    url(r'^$',
        SiteView.as_view(),
        name='front',
        kwargs={'path':'', 'action':'', 'ext':'.html'}),
    url(r'', include('ilot.api.urls') ),
    url(uuid_slug_regexp+'+\/$',
        FrontView.as_view(), name='query', kwargs={'action':'', 'ext':'/'}),
    url(uuid_slug_regexp+'+\/(?P<action>[a-zA-Z]+)\/$',
        FrontView.as_view(), name='front', kwargs={'ext':'/'}),
    url(r'(?P<path>.+)(?P<ext>(\.json|\.html|\.xml)+)$',
        SiteView.as_view(),
        name='site', kwargs={'action':'index'})

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not os.environ.get('DJANGO_ENV', 'dev') == 'production':
    urlpatterns.insert(0, url(r'admin/', include(admin.site.urls)))
