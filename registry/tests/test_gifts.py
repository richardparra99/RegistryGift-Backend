from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from registry.models import Event, Gift

class GiftAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otro', password='password123')

        self.event = Event.objects.create(
            owner=self.user,
            name="Test Event",
            description="Descripción de prueba",
            datetime="2025-08-01T18:00:00Z",
            type="birthday",
            color="red",
            private=False
        )

        self.other_event = Event.objects.create(
            owner=self.other_user,
            name="Otro Evento",
            description="Evento ajeno",
            datetime="2025-09-01T18:00:00Z",
            type="other",
            color="blue",
            private=False
        )


        self.client = APIClient()

    def authenticate(self):
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_crear_gift(self):
        self.authenticate()
        data = {
            "name": "Smartwatch",
            "description": "Un reloj inteligente",
            "quantity": 1,
            "priority": "medium",
            "event_id": self.event.id
        }
        response = self.client.post('/api/gifts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Gift.objects.count(), 1)
        gift = Gift.objects.first()
        self.assertEqual(gift.name, "Smartwatch")
        self.assertEqual(gift.event, self.event)

    def test_listar_gifts(self):
        self.authenticate()
        # Crear un gift asociado al evento
        Gift.objects.create(
        event=self.event,
        name="Libro",
        description="Libro interesante",
        quantity=2,
        priority="low"
        )
        
        response = self.client.get('/api/gifts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Libro")

    
    def test_actualizar_gift(self):
        self.authenticate()
        gift = Gift.objects.create(
        event=self.event,
        name="Cámara",
        description="Cámara digital",
        quantity=1,
        priority="high"
        )
    
        data = {"name": "Cámara HD", "quantity": 2}
        response = self.client.patch(f'/api/gifts/{gift.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gift.refresh_from_db()
        self.assertEqual(gift.name, "Cámara HD")
        self.assertEqual(gift.quantity, 2)

    
    def test_eliminar_gift(self):
        self.authenticate()
        gift = Gift.objects.create(
        event=self.event,
        name="Celular",
        description="Smartphone gama alta"
        )
        
        response = self.client.delete(f'/api/gifts/{gift.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Gift.objects.filter(id=gift.id).exists())


    def test_no_actualizar_gift_ajeno(self):
        self.authenticate()
        gift = Gift.objects.create(
        event=self.other_event,
        name="TV",
        description="Televisor 4K"
        )
        
        data = {"name": "Hackeado"}
        response = self.client.patch(f'/api/gifts/{gift.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_no_eliminar_gift_ajeno(self):
        self.authenticate()  # Nos autenticamos como self.user

        gift_ajeno = Gift.objects.create(
            event=self.other_event,
            name="Gift Ajeno",
            description="Este regalo no me pertenece"
        )

        response = self.client.delete(f'/api/gifts/{gift_ajeno.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Gift.objects.filter(id=gift_ajeno.id).exists())
        


    def test_actualizar_gift_propio(self):
        self.authenticate()
        gift = Gift.objects.create(
            event=self.event,
            name="Libro",
            description="Un libro interesante",
            quantity=1
        )

        data = {
            "name": "Libro actualizado",
            "description": "Una nueva descripción",
            "quantity": 2,
            "priority": "high"
        }

        response = self.client.patch(f'/api/gifts/{gift.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        gift.refresh_from_db()
        self.assertEqual(gift.name, "Libro actualizado")
        self.assertEqual(gift.description, "Una nueva descripción")
        self.assertEqual(gift.quantity, 2)
        self.assertEqual(gift.priority, "high")


    def test_eliminar_gift_propio(self):
        self.authenticate()
        gift = Gift.objects.create(
            event=self.event,
            name="Juego de mesa",
            description="Para jugar en grupo",
            quantity=1
        )

        response = self.client.delete(f'/api/gifts/{gift.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Gift.objects.filter(id=gift.id).exists())


    def test_crear_gift_sin_autenticacion(self):
        data = {
            "event_id": self.event.id,
            "name": "Regalo sin login",
            "description": "No debería poder crearse",
            "quantity": 1
        }

        response = self.client.post('/api/gifts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_listar_gifts_autenticado(self):
        self.authenticate()
        Gift.objects.create(event=self.event, name="Gift A", quantity=1)
        response = self.client.get('/api/gifts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_gift_cantidad_negativa(self):
        self.authenticate()
        data = {
            "event_id": self.event.id,
            "name": "Gift inválido",
            "quantity": -5
        }

        response = self.client.post('/api/gifts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)
        #se modifico GiftSimpleSerializer en la clase gift_views.py, se agrego la funcion
        #validate_quantity para que solo valide cantidad mayor o igual a 1.


    def test_gift_sin_nombre(self):
        self.authenticate()
        data = {
            "event_id": self.event.id,
            "description": "Falta el nombre",
            "quantity": 1
        }

        response = self.client.post('/api/gifts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)


    def test_gift_url_invalida(self):
        self.authenticate()
        data = {
            "event_id": self.event.id,
            "name": "Gift con URL",
            "reference_link": "no_es_una_url"
        }

        response = self.client.post('/api/gifts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reference_link", response.data)


    def test_gift_prioridad_invalida(self):
        self.authenticate()
        data = {
            "event_id": self.event.id,
            "name": "Gift con prioridad inválida",
            "priority": "extreme"
        }

        response = self.client.post('/api/gifts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("priority", response.data)



    def test_listar_gifts_evento(self):
        self.authenticate()
        Gift.objects.create(event=self.event, name="Libro", quantity=1)
        Gift.objects.create(event=self.other_event, name="TV", quantity=1)

        response = self.client.get(f'/api/gifts/?event_id={self.event.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Libro")
    

    def test_obtener_detalle_gift(self):
        self.authenticate()
        gift = Gift.objects.create(event=self.event, name="Auriculares", quantity=1)

        response = self.client.get(f'/api/gifts/{gift.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Auriculares")



    def test_actualizar_gift_no_autenticado(self):
        gift = Gift.objects.create(event=self.event, name="Libro", quantity=1)

        data = {"name": "Libro Hackeado"}
        response = self.client.patch(f'/api/gifts/{gift.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_eliminar_gift_no_autenticado(self):
        gift = Gift.objects.create(event=self.event, name="Cámara", quantity=1)

        response = self.client.delete(f'/api/gifts/{gift.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_reservar_gift_autenticado(self):
        self.authenticate()
        gift = Gift.objects.create(event=self.event, name="Puzzle", quantity=1)

        response = self.client.post(f'/api/gifts/{gift.id}/reserve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gift.refresh_from_db()
        self.assertTrue(gift.reserved)
        self.assertEqual(gift.reserved_by, self.user)


    def test_reservar_gift_sin_autenticacion(self):
        gift = Gift.objects.create(event=self.event, name="Puzzle", quantity=1)

        response = self.client.post(f'/api/gifts/{gift.id}/reserve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gift.refresh_from_db()
        self.assertTrue(gift.reserved)
        self.assertIsNone(gift.reserved_by)


    def test_reservar_gift_ya_reservado(self):
        self.authenticate()
        gift = Gift.objects.create(event=self.event, name="Puzzle", quantity=1, reserved=True)

        response = self.client.post(f'/api/gifts/{gift.id}/reserve/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
