from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets

from ilot.api.serializers import *
from ilot.rules.models import Action, Type, Attribute, Rule, Requirement, Status

class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Action.objects.all()
    serializer_class = ActionSerializer

class StatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

class RuleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
