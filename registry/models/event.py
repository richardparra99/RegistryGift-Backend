from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
  EVENT_TYPES = [
		('birthday', 'Cumpleaños'),
		('wedding', 'Matrimonio'),
		('anniversary', 'Aniversario'),
		('other', 'Otro'),
	]
  
  COLOR_TYPES = [
      ('red', 'Rojo'),
      ('blue', 'Azul'),
      ('green', 'Verde'),
      ('orange', 'Naranja'),
      ('purple', 'Morado'),
      ('yellow', 'Amarillo'),
      ('pink', 'Rosa'),
      ('gray', 'Gris'),
      ('teal', 'Turquesa'),
      ('brown', 'Marrón'),
  ]
  
  owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
  name = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  datetime = models.DateTimeField()
  type = models.CharField(max_length=20, choices=EVENT_TYPES, default='birthday')
  color = models.CharField(max_length=20, choices=COLOR_TYPES, default='red')
  private = models.BooleanField(default=False)
  
  def __str__(self):
    return f"{self.name} ({self.type})"