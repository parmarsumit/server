from rest_framework import serializers
from ilot.rules.models import Action, Type, Attribute, Rule, Status

from ilot.core.models import Moderation, Translation, Item

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields =  '__all__'

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields =  '__all__'

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields =  '__all__'




class ModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderation
        fields = '__all__'# ('id', 'origin', 'target', 'related', )

class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__' #('id', 'title', 'image', 'parent', 'get_data', )
