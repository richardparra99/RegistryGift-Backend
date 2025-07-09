from rest_framework import serializers
from registry.models import Event, Comment, Gift
from django.contrib.auth.models import User

class UserSimpleSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username')

class EventSimpleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = '__all__'
    
class CommentSimpleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Comment
    fields = '__all__'
    
class GiftSimpleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Gift
    fields = '__all__'

  def validate_quantity(self, value):
      if value < 1:
          raise serializers.ValidationError("La cantidad debe ser mayor o igual a 1.")
      return value
