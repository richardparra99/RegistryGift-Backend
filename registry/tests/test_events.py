from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from registry.models import Event


class EventAPITestCase(APITestCase):
  # Datos de inicio, se vuelven a crear antes de cada test
  def setUp(self):
    self.user = User.objects.create_user(username='unit_user', password='password123')
    self.otro_user = User.objects.create_user(username='otro_unit_user', password='password123')
    self.client = APIClient()
    self.events = {
      "mi_publico": Event.objects.create(
        owner=self.user,
        name="Mi publico",
        description="Evento publico de unit_user",
        datetime="2025-07-01T18:00:00Z",
        type="birthday",
        private=False
      ),
      "otro_publico": Event.objects.create(
        owner=self.otro_user,
        name="Otro publico",
        description="Evento publico de otro_unit_user",
        datetime="2025-07-02T18:00:00Z",
        type="wedding",
        private=False
      ),
      "mi_privado": Event.objects.create(
        owner=self.user,
        name="Mi privado",
        description="Evento privado de unit_user",
        datetime="2025-07-03T18:00:00Z",
        type="anniversary",
        private=True
      ),
      "otro_privado": Event.objects.create(
        owner=self.otro_user,
        name="Otro private",
        description="Evento privado de otro_unit_user",
        datetime="2025-07-04T18:00:00Z",
        type="other",
        private=True
      ),
    }

  # Autenticación para tests que requieren usuario autenticado
  def authenticate(self, username='unit_user', password='password123'):
    response = self.client.post('/api/token/', {
      'username': username,
      'password': password
    }, format='json')
    access = response.data['access']
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

  # GET /api/events/ para listar eventos sin autenticación, debe mostrar solo eventos públicos
  def test_lista_eventos_publicos(self):
    response = self.client.get('/api/events/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    names = [event['name'] for event in response.data]
    self.assertIn("Mi publico", names)
    self.assertIn("Otro publico", names)
    self.assertNotIn("Mi privado", names)
    self.assertNotIn("Otro privado", names)

  # GET /api/events/ para listar eventos con autenticación, debe mostrar eventos públicos y privados del usuario autenticado
  def test_lista_eventos_authenticated(self):
    self.authenticate()
    response = self.client.get('/api/events/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    names = [event['name'] for event in response.data]
    self.assertIn("Mi publico", names)
    self.assertIn("Otro publico", names)
    self.assertIn("Mi privado", names)
    self.assertNotIn("Otro privado", names)

  # POST /api/events/ para crear un evento, requiere autenticación, debe asignar el usuario autenticado como owner
  def test_crear_evento(self):
    self.authenticate()
    data = {
      "name": "Nuevo Evento",
      "description": "Un evento nuevo",
      "datetime": "2025-08-01T18:00:00Z",
      "type": "wedding",
      "private": False
    }
    response = self.client.post('/api/events/', data, format='json')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(Event.objects.count(), 5)
    self.assertEqual(Event.objects.last().owner, self.user)

  # PATCH /api/events/<id>/ para actualizar un evento propio, debe permitir la actualización
  def test_actualizar_evento_propio(self):
    self.authenticate()
    event_id = self.events["mi_publico"].id
    data = {"name": "Evento Actualizado"}
    response = self.client.patch(f'/api/events/{event_id}/', data, format='json')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.events["mi_publico"].refresh_from_db()
    self.assertEqual(self.events["mi_publico"].name, "Evento Actualizado")

  #  PATCH /api/events/<id>/ para actualizar un evento ajeno, debe denegar la actualización
  def test_actualizar_evento_ajeno(self):
    self.authenticate(username='otro_unit_user', password='password123')
    event_id = self.events["mi_publico"].id
    data = {"name": "Evento Hackeado"}
    response = self.client.patch(f'/api/events/{event_id}/', data, format='json')
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

  # DELETE /api/events/<id>/ para eliminar un evento propio, debe permitir la eliminación
  def test_eliminar_evento_propio(self):
    self.authenticate()
    event_id = self.events["mi_privado"].id
    response = self.client.delete(f'/api/events/{event_id}/')
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    self.assertFalse(Event.objects.filter(id=event_id).exists())
    
  # DELETE /api/events/<id>/ para eliminar un evento publico ajeno, debe denegar la eliminación
  def test_eliminar_evento_publico_ajeno(self):
    self.authenticate(username='otro_unit_user', password='password123')
    event_id = self.events["mi_publico"].id
    response = self.client.delete(f'/api/events/{event_id}/')
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

  # DELETE /api/events/<id>/ para eliminar un evento privado ajeno, debe denegar la eliminación
  def test_eliminar_evento_privado_ajeno(self):
    self.authenticate(username='otro_unit_user', password='password123')
    event_id = self.events["mi_privado"].id
    response = self.client.delete(f'/api/events/{event_id}/')
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
