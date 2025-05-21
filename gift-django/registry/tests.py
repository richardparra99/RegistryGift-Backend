from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from django.test import TestCase
from django.contrib.auth.models import User
from registry.models.event import Event
from datetime import datetime

class EventoModelTest(TestCase):
    def test_crear_evento(self):
        user = User.objects.create_user(username="juan", password="1234")
        evento = Event.objects.create(
            owner=user,
            name="Cumpleaños de Ana",
            description="Fiesta sorpresa en el jardín",
            datetime=datetime(2025, 8, 20, 18, 0)
        )
        self.assertEqual(evento.name, "Cumpleaños de Ana")
        self.assertEqual(evento.description, "Fiesta sorpresa en el jardín")
        self.assertEqual(str(evento.datetime.date()), "2025-08-20")
        self.assertEqual(str(evento), "Cumpleaños de Ana (birthday)")



from registry.models.gift import Gift  # asegurate de importar el modelo

class GiftModelTest(TestCase):
    def test_crear_gift(self):
        user = User.objects.create_user(username="lucia", password="abcd")
        evento = Event.objects.create(
            owner=user,
            name="Baby Shower",
            description="Regalos para el bebé",
            datetime=datetime(2025, 9, 10, 15, 0)
        )
        regalo = Gift.objects.create(
            name="Pañalera decorada",
            description="Con ositos de peluche",
            event=evento
        )
        self.assertEqual(regalo.name, "Pañalera decorada")
        self.assertEqual(regalo.description, "Con ositos de peluche")
        self.assertEqual(regalo.event.name, "Baby Shower")



class EventApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="mario", password="1234")
        self.client.force_authenticate(user=self.user)

    def test_crear_evento_por_api(self):
        url = "/api/events/"
        data = {
            "owner": self.user.id,
            "name": "Conferencia de tecnología",
            "description": "Evento para desarrolladores",
            "datetime": "2025-11-15T09:00:00"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().name, "Conferencia de tecnología")



#python manage.py test