from django.db import models
from django.contrib.auth.models import User
from registry.models import Event


class Gift(models.Model):
  PRIORITIES = [
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
  ]
  
  event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gifts')
  name = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  quantity = models.IntegerField(default=1)
  reference_link = models.URLField(blank=True,  null=True)
  priority = models.CharField(max_length=10, choices=PRIORITIES, blank=True, null=True)
  reserved_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='reserved_gifts')
  reserved = models.BooleanField(default=False)
  
  def __str__(self):
    return f"{self.name} - {self.event.name}"