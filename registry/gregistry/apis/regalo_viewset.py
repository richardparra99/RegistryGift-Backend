from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action

from gregistry.models.regalo import Regalo
from gregistry.models.evento import Evento

# Serializador de lectura
class RegaloSerializer(serializers.ModelSerializer):
    reservado_por = serializers.StringRelatedField()
    evento = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Regalo
        fields = [
            'id', 'nombre', 'descripcion', 'url', 'cantidad_deseada', 'prioridad',
            'reservado', 'reservado_por', 'evento', 'creado_en'
        ]


# Serializador de escritura
class RegaloCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regalo
        fields = [
            'nombre', 'descripcion', 'url', 'cantidad_deseada', 'prioridad', 'evento'
        ]


class RegaloViewSet(viewsets.ModelViewSet):
    queryset = Regalo.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Regalo.objects.select_related("evento", "reservado_por")

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RegaloSerializer
        return RegaloCreateUpdateSerializer

    def perform_create(self, serializer):
        evento = serializer.validated_data['evento']
        if evento.creado_por != self.request.user:
            raise PermissionDenied("Solo el creador del evento puede agregar regalos.")
        serializer.save()

    def perform_update(self, serializer):
        regalo = self.get_object()
        if regalo.evento.creado_por != self.request.user:
            raise PermissionDenied("No tienes permiso para modificar este regalo.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.evento.creado_por != self.request.user:
            raise PermissionDenied("No tienes permiso para eliminar este regalo.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reservar(self, request, pk=None):
        regalo = self.get_object()
        if regalo.reservado:
            return Response({"detail": "Este regalo ya fue reservado."}, status=400)
        regalo.reservado = True
        regalo.reservado_por = request.user
        regalo.save()
        return Response({"detail": "Regalo reservado correctamente."})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancelar_reserva(self, request, pk=None):
        regalo = self.get_object()
        if regalo.reservado_por != request.user:
            raise PermissionDenied("No puedes cancelar la reserva de otro usuario.")
        regalo.reservado = False
        regalo.reservado_por = None
        regalo.save()
        return Response({"detail": "Reserva cancelada correctamente."})
