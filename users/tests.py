from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import Client

User = get_user_model()

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

    def test_user_registration(self):
        response = self.client.post('/api/users/register/', self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        response = self.client.post('/api/users/login/', {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_invalid_credentials(self):
        response = self.client.post('/api/users/login/', {'username': 'nonexistentuser', 'password': 'wrongpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', email='test@example.com', first_name='Test', last_name='User', is_staff=True)
        self.client = Client()

    def test_user_admin_list_display(self):
        self.client.login(username='admin', password='your_admin_password')

        response = self.client.get(reverse('admin:auth_user_changelist'))

        self.assertContains(response, 'username')
        self.assertContains(response, 'email')
        self.assertContains(response, 'first_name')
        self.assertContains(response, 'last_name')
        self.assertContains(response, 'is_staff')
        self.assertContains(response, 'date_joined')