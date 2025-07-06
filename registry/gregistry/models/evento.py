from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('CUMPLEAÑOS', 'Cumpleaños'),
        ('BODA', 'Boda'),
        ('BABY_SHOWER', 'Baby Shower'),
        ('NAVIDAD', 'Navidad'),
        ('OTRO', 'Otro'),
    ]

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos')

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"
