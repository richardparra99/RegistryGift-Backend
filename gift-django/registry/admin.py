from django.contrib import admin
from .models import Event, Comment, Gift

admin.site.register(Event)
admin.site.register(Comment)
admin.site.register(Gift)