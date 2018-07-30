from ilot.core.models import Moderation, Translation, Item, request_switch
from ilot.models import filter_with_perm
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
request_switch.organization = None
request_switch.profile = None

class ModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderation
        read_only_fields = ('action', 'status',)
        fields = '__all__'# ('id', 'origin', 'target', 'related', )

class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        read_only_fields = ('action', 'status',)
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        read_only_fields = ('action', 'status',)
        fields = '__all__' #('id', 'title', 'image', 'parent', 'get_data', )



class ModerationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Moderation.objects.all()
    serializer_class = ModerationSerializer

class TranslationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer

class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    #filter_backends = (DjangoFilterBackend,)
    #filter_fields = ('status', 'action')
    #search_fields = ('status', 'action')
    #ordering_fields = ('status', 'action')
