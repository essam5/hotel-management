from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Reservation
from django.contrib.auth.models import User
from rooms.models import Room
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model


User = get_user_model()

class ReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.room = Room.objects.create(room_number='101', room_type='single', price_per_night='100.00', max_occupancy=2)
        self.reservation_data = {
            'user': self.user.id,
            'room': self.room.id,
            'status': 'pending',
            'guests': 2,
            'check_in_date': '2023-10-01',
            'check_out_date': '2023-10-10',
        }

    def test_create_reservation(self):
        response = self.client.post('/api/reservations/', self.reservation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_create_reservation_invalid_room(self):
        self.room.delete()
        response = self.client.post('/api/reservations/', self.reservation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation_overlapping_dates(self):
        Reservation.objects.create(**self.reservation_data)
        overlapping_reservation_data = {
            'user': self.user.id,
            'room': self.room.id,
            'status': 'pending',
            'guests': 2,
            'check_in_date': '2023-10-05',
            'check_out_date': '2023-10-15',
        }
        response = self.client.post('/api/reservations/', overlapping_reservation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_reservation(self):
        reservation = Reservation.objects.create(**self.reservation_data)
        response = self.client.delete(f'/api/reservations/{reservation.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ReservationAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='admin', password='admin_password', is_staff=True, is_superuser=True)
        self.room = Room.objects.create(room_number='101', room_type='single', price_per_night='100.00', max_occupancy=2)
        self.reservation = Reservation.objects.create(user=self.user, room=self.room, status='pending', guests=2, check_in_date='2023-10-01', check_out_date='2023-10-10')
        self.client = Client()

    def test_reservation_admin_list_display(self):
        self.client.login(username='admin', password='admin_password')

        response = self.client.get(reverse('admin:reservation_reservation_changelist'))

        self.assertContains(response, 'user')
        self.assertContains(response, 'room')
        self.assertContains(response, 'check_in_date')
        self.assertContains(response, 'check_out_date')
        self.assertContains(response, 'status')

    def test_reservation_admin_save_model(self):
        self.client.login(username='admin', password='admin_password')

        response = self.client.post(reverse('admin:reservation_reservation_add'), {
            'user': self.user.id,
            'room': self.room.id,
            'status': 'pending',
            'guests': 2,
            'check_in_date': '2023-10-05',
            'check_out_date': '2023-10-15',
        })

        self.assertEqual(Reservation.objects.count(), 1)

    def test_reservation_admin_save_model_non_overlapping(self):
        self.client.login(username='admin', password='admin_password')

        response = self.client.post(reverse('admin:reservation_reservation_add'), {
            'user': self.user.id,
            'room': self.room.id,
            'status': 'pending',
            'guests': 2,
            'check_in_date': '2023-10-15',
            'check_out_date': '2023-10-25',
        })

        self.assertEqual(Reservation.objects.count(), 2)