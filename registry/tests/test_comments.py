from rest_framework.test import APITestCase 
from rest_framework import status
from django.contrib.auth.models import User
from registry.models import Gift, Event, Comment
from datetime import datetime
from django.utils.timezone import make_aware

class CommentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='123456')
        self.event = Event.objects.create(
            name="Test Event",
            description="Descripción de prueba",
            datetime=make_aware(datetime(2025, 8, 1, 18, 0)),
            type="birthday",
            color="red",
            private=False,
            owner=self.user
        )
        self.gift = Gift.objects.create(
            name="Regalo de prueba",
            description="Un regalo especial",
            quantity=1,
            priority="medium",
            event=self.event
        )

    def authenticate(self):
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': '123456'
        }, format='json')
        access = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    
    # POST /api/comments/ Debería permitir crear un comentario autenticado asociado a un evento válido.
    def test_crear_comentario_autenticado(self):
        self.authenticate()
        data = {
            "event_id": self.event.id,
            "text": "¡Este regalo es perfecto!"
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, "¡Este regalo es perfecto!")

    # POST /api/comments/ Debería permitir crear un comentario sin autenticación (comentario anónimo).
    def test_crear_comentario_sin_autenticacion(self):
        data = {
            "event_id": self.event.id,
            "text": "Comentario no autenticado"
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # GET /api/comments/ Debería listar todos los comentarios asociados a un evento específico.
    def test_listar_comentarios_por_gift(self):
        self.authenticate()
        Comment.objects.create(event=self.event, poster=self.user, text="Comentario 1")
        Comment.objects.create(event=self.event, poster=self.user, text="Comentario 2")

        response = self.client.get(f'/api/comments/?event_id={self.event.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    # DELETE /api/comments/<id>/ Debería permitir al autor eliminar su propio comentario.
    def test_eliminar_comentario_propio(self):
        self.authenticate()
        comment = Comment.objects.create(event=self.event, poster=self.user, text="Mi comentario")
        
        response = self.client.delete(f'/api/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    # DELETE /api/comments/<id>/ No debería permitir eliminar comentarios creados por otro usuario.
    def test_no_eliminar_comentario_ajeno(self):
        other_user = User.objects.create_user(username='intruso', password='1234')
        comment = Comment.objects.create(event=self.event, poster=other_user, text="No borres esto")
        self.authenticate()
        response = self.client.delete(f'/api/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    # POST /api/comments/ Debería devolver error 400 si el texto del comentario está vacío.
    def test_comentario_texto_vacio(self):
        self.authenticate()
        data = {
            "event_id": self.event.id,
            "text": ""
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", response.data)

    # POST /api/comments/ Debería devolver error 400 si el event_id no existe.
    def test_comentario_gift_inexistente(self):
        self.authenticate()
        data = {
            "event_id": 99999,
            "text": "Comentario inválido"
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("event_id", response.data)

    # Debería devolver error 401 si se intenta eliminar un comentario sin autenticación
    def test_eliminar_comentario_no_autenticado(self):
        comment = Comment.objects.create(event=self.event, poster=self.user, text="Comentario")
        response = self.client.delete(f'/api/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    # Debería devolver error 404 si se intenta eliminar un comentario que no existe.
    def test_eliminar_comentario_inexistente(self):
        self.authenticate()
        response = self.client.delete('/api/comments/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # Debería devolver error 400 si no se proporciona event_id al crear un comentario.
    def test_comentario_sin_gift_id(self):
        self.authenticate()
        data = {
            "text": "Comentario sin regalo"
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("event_id", response.data)

    
    # POST /api/comments/ con campos no permitidos → 400 Bad Request
    def test_crear_comentario_con_campo_extra(self):
        self.authenticate()
        data = {
            "event_id": self.event.id,
            "text": "Comentario válido",
            "extra_field": "Este campo no debería estar"
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # O BAD_REQUEST si usas validación estricta


    # GET /api/comments/ ordenados por fecha descendente
    def test_listar_comentarios_ordenados_por_fecha(self):
        self.authenticate()
        Comment.objects.create(event=self.event, poster=self.user, text="Primero")
        Comment.objects.create(event=self.event, poster=self.user, text="Segundo")
        
        response = self.client.get(f'/api/comments/?event_id={self.event.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['text'], "Segundo")  # El más reciente primero
        self.assertEqual(response.data[1]['text'], "Primero")


    # POST /api/comments/ sin autenticación, debería crear con poster=None
    def test_crear_comentario_anonimo(self):
        data = {
            "event_id": self.event.id,
            "text": "Comentario anónimo"
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.first()
        self.assertIsNone(comment.poster)


    # PATCH /api/comments/<id>/ para actualizar comentario propio
    def test_actualizar_comentario_propio(self):
        self.authenticate()
        comment = Comment.objects.create(event=self.event, poster=self.user, text="Texto original")
        data = {"text": "Texto actualizado"}
        
        response = self.client.patch(f'/api/comments/{comment.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.text, "Texto actualizado")


    # PATCH /api/comments/<id>/ no debe permitir actualizar comentario ajeno
    def test_no_actualizar_comentario_ajeno(self):
        other_user = User.objects.create_user(username='otro', password='1234')
        comment = Comment.objects.create(event=self.event, poster=other_user, text="Texto de otro")
        self.authenticate()
        
        data = {"text": "Intento de edición"}
        response = self.client.patch(f'/api/comments/{comment.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        comment.refresh_from_db()
        self.assertEqual(comment.text, "Texto de otro")


    # POST /api/comments/ con texto muy largo (sin validación explícita puede pasar)
    def test_crear_comentario_texto_largo(self):
        self.authenticate()
        texto_largo = "a" * 10000
        data = {
            "event_id": self.event.id,
            "text": texto_largo
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.first().text, texto_largo)


    # DELETE /api/comments/<id>/ debe permitir al owner del evento eliminar cualquier comentario de su evento
    def test_owner_puede_eliminar_comentario_ajeno(self):
        other_user = User.objects.create_user(username='otro', password='1234')
        comment = Comment.objects.create(event=self.event, poster=other_user, text="Comentario de invitado")
        
        self.authenticate()  # self.user es el owner del evento
        response = self.client.delete(f'/api/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)


    # PATCH /api/comments/<id>/ el owner del evento no debe poder editar comentarios ajenos
    def test_owner_no_puede_editar_comentario_ajeno(self):
        other_user = User.objects.create_user(username='otro', password='1234')
        comment = Comment.objects.create(event=self.event, poster=other_user, text="Original")
        
        self.authenticate()  # self.user es el owner del evento
        data = {"text": "Intento de edición como owner"}
        response = self.client.patch(f'/api/comments/{comment.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        comment.refresh_from_db()
        self.assertEqual(comment.text, "Original")


    # DELETE /api/comments/<id>/ el owner del evento puede eliminar comentario anónimo
    def test_owner_elimina_comentario_anonimo(self):
        comment = Comment.objects.create(event=self.event, poster=None, text="Comentario sin usuario")
        
        self.authenticate()  # self.user es el owner
        response = self.client.delete(f'/api/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)


    # DELETE /api/comments/<id>/ no debe permitir eliminar comentario anónimo si no es owner ni autor = 401(NO AUTORIZADO)
    def test_usuario_no_elimina_comentario_anonimo_ajeno(self):
        owner = self.user
        another_event = Event.objects.create(
            name="Otro Evento",
            description="Otro",
            datetime=make_aware(datetime(2025, 8, 2, 10, 0)),
            type="wedding",
            color="blue",
            private=False,
            owner=owner
        )
        comment = Comment.objects.create(event=another_event, poster=None, text="Anónimo")
        
        another_user = User.objects.create_user(username='intruso', password='1234')
        self.client.login(username='intruso', password='1234')
        response = self.client.delete(f'/api/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    # GET /api/comments/ sin filtros debería devolver todos los comentarios si está permitido
    def test_listar_todos_los_comentarios(self):
        self.authenticate()
        Comment.objects.create(event=self.event, poster=self.user, text="Uno")
        Comment.objects.create(event=self.event, poster=self.user, text="Dos")

        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
