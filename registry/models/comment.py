from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
  event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='comments')
  poster = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='comments')
  text = models.TextField()
  posttime = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f"{self.event.name} | {self.poster.username if self.poster else 'Anonymous'}: {self.text[:20]}..."
