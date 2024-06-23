# streaming/tests/test_views.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

class AuthTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.user_data = {
            "username": "kenan",
            "password": "password123",
            "email": "adityapfm99@gmail.com"
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_obtain_pair(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.token_url, {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.token_url, {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }, format='json')
        refresh_token = response.data['refresh']
        
        response = self.client.post(self.refresh_url, {
            "refresh": refresh_token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
