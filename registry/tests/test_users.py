from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class UserAPITestCase(APITestCase):

    # POST /api/auth/register/
    def test_registro_exitoso(self):
        data = {
            "username": "nuevo_usuario",
            "password": "clave123",
            "email": "nuevo@ejemplo.com"
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="nuevo_usuario").exists())

    def test_registro_sin_password(self):
        data = {
            "username": "usuario_sin_pass",
            "email": "sinpass@ejemplo.com"
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_username_duplicado(self):
        User.objects.create_user(username='repetido', password='pass', email='repetido@ejemplo.com')
        data = {
            "username": "repetido",
            "password": "otra_clave",
            "email": "otro@ejemplo.com"
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # GET /api/auth/me/
    def test_me_autenticado(self):
        user = User.objects.create_user(username='yo', password='123456', email='yo@ejemplo.com')
        response = self.client.post('/api/token/', {'username': 'yo', 'password': '123456'}, format='json')
        access = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'yo')

    def test_me_sin_autenticacion(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
