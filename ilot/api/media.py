
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from ilot.medias.models import Media
from ilot.core.models import request_switch


class MediaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Media
        read_only_fields = ('id', 'actor',)
        fields = '__all__'


class MediaViewSet(ModelViewSet):

    queryset = Media.objects.none()

    def get_queryset(self):
        return Media.objects.filter(actor=request_switch.akey)

    serializer_class = MediaSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        serializer.save(actor=self.request.session.get('akey'),
                        item=self.request.data.get('item'),
                        image=self.request.data.get('image'),
                        file=self.request.data.get('file'))
