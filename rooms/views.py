
from rest_framework import generics, permissions
from .models import Room
from .serializers import RoomSerializer
from rest_framework import serializers
from django.utils import timezone
from reservations.models import Reservation
from django.db.models import Q
from reservations.permissions import IsAdminOrReadOnly

import logging

logger = logging.getLogger(__name__)


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    
    def perform_create(self, serializer):
        # Ensure room number is unique
        room_number = serializer.validated_data['room_number']
        if Room.objects.filter(room_number=room_number).exists():
            raise serializers.ValidationError({'room_number': 'Room with this number already exists.'})
        
        serializer.save()
        logger.info(f"Room added: {serializer.data}")
        
class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdminOrReadOnly]
    

class AvailableRoomsListView(generics.ListAPIView):
    serializer_class = RoomSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        # Check if start_date and end_date are present in the request
        if not (start_date_str and end_date_str):
            return Room.objects.none()  

        # Convert date strings to datetime objects
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Room.objects.none()  

        # Query rooms that are available for the specified date range
        reserved_rooms = Reservation.objects.filter(
           (Q(check_in_date__lte=start_date, check_out_date__gte=start_date) |
             Q(check_in_date__lte=end_date, check_out_date__gte=end_date) |
             Q(check_in_date__gte=start_date, check_out_date__lte=end_date))
        ).values_list('room_id', flat=True)
        
        available_rooms = Room.objects.exclude(id__in=reserved_rooms)

        return available_rooms
  