from rest_framework import viewsets, serializers, status
from registry.models import Gift, Event
from registry.api import EventSimpleSerializer, UserSimpleSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

class GiftSerializer(serializers.ModelSerializer):
  event = EventSimpleSerializer(read_only=True)
  event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), write_only=True)
  
  reserved_by = UserSimpleSerializer(read_only=True)
  
  class Meta:
    model = Gift
    fields = ('id', 'event', 'event_id', 'name', 'description', 'quantity', 'reference_link', 'priority', 'reserved_by', 'reserved')
  
  def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser mayor o igual a 1.")
        return value

class GiftViewSet(viewsets.ModelViewSet):
  serializer_class = GiftSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]
  
  def get_queryset(self):
    event_id = self.request.query_params.get('event_id')
    if event_id:
      return Gift.objects.filter(event__id=event_id)
    return Gift.objects.all()
  
  def perform_create(self, serializer):
    event_id = self.request.data.get('event_id')
    try:
      event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
      raise serializers.ValidationError({'event_id': 'Este Evento no existe'})
    if event.owner != self.request.user:
      raise PermissionDenied({'error': 'Este evento no te pertenece.'})
    serializer.save(event_id=self.request.data.get('event_id'))
    
  def perform_update(self, serializer):
    event = self.get_object().event
    if event.owner != self.request.user:
      raise PermissionDenied({'error': 'Este evento no te pertenece.'})
    serializer.save()
    
  def perform_destroy(self, instance):
    if instance.event.owner != self.request.user:
      raise PermissionDenied({'error': 'Este evento no te pertenece.'})
    instance.delete()
    
  @action(detail=True, methods=['post'], url_path='reserve', permission_classes=[AllowAny])
  def reserve(self, request, pk=None):
    gift = self.get_object()
    
    if gift.reserved:
      return Response({'error': 'Este regalo ya está reservado.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user.is_authenticated:
      gift.reserved_by = request.user
    else:
      gift.reserved_by = None
    
    gift.reserved = True  
    gift.save()
    return Response({'message': 'Reserva exitosa.'}, status=status.HTTP_200_OK)
