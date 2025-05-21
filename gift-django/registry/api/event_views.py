from rest_framework import viewsets, serializers
from registry.models import Event
from registry.api import CommentSimpleSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

class EventSerializer(serializers.ModelSerializer):
  comments = CommentSimpleSerializer(many=True, read_only=True)
  
  class Meta:
    model = Event
    fields = ('id', 'name', 'description', 'datetime', 'type', 'private', 'owner', 'comments')
    
class EventViewSet(viewsets.ModelViewSet):
  serializer_class = EventSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]
  
  def get_queryset(self):
    return Event.objects.filter(private=False).order_by('-datetime')
  
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