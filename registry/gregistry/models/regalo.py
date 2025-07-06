from django.db import models
from django.contrib.auth.models import User
from gregistry.models.evento import Evento

class Regalo(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    url = models.URLField(blank=True)
    cantidad_deseada = models.PositiveIntegerField(default=1)
    prioridad = models.CharField(
        max_length=20,
        blank=True,
        choices=[("ALTA", "Alta"), ("MEDIA", "Media"), ("BAJA", "Baja")]
    )
    reservado = models.BooleanField(default=False)
    reservado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='regalos_reservados')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='regalos')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({'Reservado' if self.reservado else 'Disponible'})"

