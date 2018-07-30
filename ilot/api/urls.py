from django.conf.urls import *  # NOQA
from ilot.api.views import *
from ilot.api.media import MediaViewSet
from rest_framework.authtoken import views

#
from rest_framework import routers
router = routers.DefaultRouter()

#
router.register(r'rules/actions', ActionViewSet)
router.register(r'rules/attributes', AttributeViewSet)
router.register(r'rules/status', StatusViewSet)
router.register(r'rules/types', TypeViewSet)
router.register(r'rules/rules', RuleViewSet)
#
#router.register(r'grammar/notifications', StatusViewSet)
#router.register(r'grammar/messages', StatusViewSet)
#router.register(r'grammar/panels', StatusViewSet)

router.register(r'media/upload', MediaViewSet)

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='ILOT API')

urlpatterns = (
        url(r'^swagger/$', schema_view),
        url(r'^', include(router.urls)),
#        url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
#        url(r'^auth/token/', views.obtain_auth_token),
)
