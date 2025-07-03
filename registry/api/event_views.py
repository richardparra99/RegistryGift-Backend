from rest_framework import viewsets, serializers
from registry.models import Event
from registry.api import CommentSimpleSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db import models

class EventSerializer(serializers.ModelSerializer):
  comments = CommentSimpleSerializer(many=True, read_only=True)
  owner = serializers.PrimaryKeyRelatedField(read_only=True)
  datetime = serializers.DateTimeField(error_messages={'invalid': 'La fecha tiene un formato incorrecto. Ejemplo de formato válido: 2025-07-01T18:00:00Z'})
  
  class Meta:
    model = Event
    fields = ('id', 'name', 'description', 'datetime', 'type', 'private', 'owner', 'comments')
    
class EventViewSet(viewsets.ModelViewSet):
  serializer_class = EventSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]
  
  def get_queryset(self):
    user = self.request.user
    if user.is_authenticated:
      return Event.objects.filter(
        models.Q(private=False) | models.Q(owner=user)
      )
    return Event.objects.filter(private=False)
  
  def perform_create(self, serializer):
    serializer.save(owner=self.request.user)
    
  def perform_update(self, serializer):
    event = self.get_object()
    if event.owner != self.request.user:
      raise PermissionDenied({'error': 'You are not the event owner'})
    serializer.save()
    
  def perform_destroy(self, instance):
    if instance.owner != self.request.user:
      raise PermissionDenied({'error': 'You are not the event owner'})
    instance.delete()
  
  @action(detail=False, methods=['get'], url_path='my', permission_classes=[IsAuthenticated])
  def my_events(self, request):
    events = Event.objects.filter(owner=request.user).order_by('-datetime')
    serializer = self.get_serializer(events, many=True)
    return Response(serializer.data)