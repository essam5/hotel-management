from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Room
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

class RoomTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.room_data = {
            'room_number': '101',
            'room_type': 'single',
            'price_per_night': '100.00',
            'max_occupancy': 2,
        }

    def test_create_room(self):
        response = self.client.post('/api/rooms/', self.room_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_create_duplicate_room(self):
        Room.objects.create(**self.room_data)
        response = self.client.post('/api/rooms/', self.room_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_available_rooms(self):
        Room.objects.create(**self.room_data)
        response = self.client.get('/api/rooms/available/?start_date=2023-10-01&end_date=2023-10-10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RoomAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='admin', password='admin_password', is_staff=True, is_superuser=True)
        self.room = Room.objects.create(room_number='101', room_type='single', price_per_night='100.00', max_occupancy=2)
        self.client = Client()

    def test_room_admin_list_display(self):
        # Log in as a superuser (admin)
        self.client.login(username='admin', password='admin_password')

        # Access the Room list page in the admin panel
        response = self.client.get(reverse('admin:room_room_changelist'))

        # Check if the custom list display fields are present in the response
        self.assertContains(response, 'room_number')
        self.assertContains(response, 'room_type')
        self.assertContains(response, 'price_per_night')
        self.assertContains(response, 'availability')
        self.assertContains(response, 'max_occupancy')