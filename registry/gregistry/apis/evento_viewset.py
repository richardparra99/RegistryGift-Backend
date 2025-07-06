from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from gregistry.models.evento import Evento
from gregistry.permissions import ReadOnlyOrDjangoModelPermissions


# SERIALIZADOR DE LECTURA
class EventoSerializer(serializers.ModelSerializer):
    creado_por = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'descripcion', 'fecha', 'tipo', 'creado_por']


# SERIALIZADOR DE ESCRITURA
class EventoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['nombre', 'descripcion', 'fecha', 'tipo']


# VIEWSET
class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == 'mis_eventos' and self.request.user.is_authenticated:
            return Evento.objects.filter(creado_por=self.request.user)
        return Evento.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'mis_eventos']:
            return EventoSerializer
        return EventoCreateSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    def perform_update(self, serializer):
        if self.get_object().creado_por != self.request.user:
            raise PermissionDenied("No tienes permiso para modificar este evento.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.creado_por != self.request.user:
            raise PermissionDenied("No tienes permiso para eliminar este evento.")
        instance.delete()

    @action(detail=False, methods=['get'], url_path='mis-eventos', permission_classes=[IsAuthenticated])
    def mis_eventos(self, request):
        eventos = Evento.objects.filter(creado_por=request.user)
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data)
