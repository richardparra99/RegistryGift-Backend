from rest_framework import viewsets, serializers
from registry.models import Comment, Event
from registry.api import EventSimpleSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.exceptions import PermissionDenied

class CommentSerializer(serializers.ModelSerializer):
  event = EventSimpleSerializer(read_only=True)
  event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), write_only=True)
  
  poster = serializers.PrimaryKeyRelatedField(read_only=True)
  
  class Meta:
    model = Comment
    fields = ('id', 'event', 'event_id', 'poster', 'text', 'posttime')

class CommentViewSet(viewsets.ModelViewSet):
  serializer_class = CommentSerializer
  
  def get_permissions(self):
    if self.action == 'create':
      return [AllowAny()]
    return [IsAuthenticatedOrReadOnly()]
  
  def get_queryset(self):
    event_id = self.request.query_params.get('event_id')
    if event_id:
      return Comment.objects.filter(event__id=event_id).order_by('-posttime')
    return Comment.objects.all().order_by('-posttime')
  
  def perform_create(self, serializer):
    serializer.save(
      event_id=self.request.data.get('event_id'),
      poster=self.request.user if self.request.user.is_authenticated else None
    )
    
  def perform_update(self, serializer):
    comment = self.get_object()
    if comment.poster != self.request.user:
      raise PermissionDenied({'error': 'Este comentario no te pertenece.'})
    serializer.save()
    
  def perform_destroy(self, request, *args, **kwargs):
    comment = self.get_object()
    user = request.user
    
    if comment.poster == user or (comment.event.owner == user):
      return super().destroy(request, *args, **kwargs)
    raise PermissionDenied({'error': 'No eres el propietario del evento ni el autor del comentario.'})
