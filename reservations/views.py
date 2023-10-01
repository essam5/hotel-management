from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .models import  Reservation
from rooms.models import Room
from .serializers import  ReservationSerializer
from rest_framework import permissions
from .permissions import IsAdminOrReadOnly
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

import logging

logger = logging.getLogger(__name__)

def is_reserved(room, check_in_date, check_out_date):
    reservations_overlap = Reservation.objects.filter(
        Q(room=room) &
        (
            (Q(check_in_date__lte=check_in_date, check_out_date__gte=check_in_date) |
             Q(check_in_date__lte=check_out_date, check_out_date__gte=check_out_date) |
             Q(check_in_date__gte=check_in_date, check_out_date__lte=check_out_date))
        )
    )
    return reservations_overlap.exists()

class ReservationListCreateView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if the room is available for the specified date range
        room_number = request.data.get('room')
        check_in_date = request.data.get('check_in_date')
        check_out_date = request.data.get('check_out_date')
        try:
            room = Room.objects.get(room_number=room_number)
        except   ObjectDoesNotExist  :
            return Response({'error': 'no room with this number.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if room.availability != 'available':
            return Response({'error': 'Room is not available for reservation.'}, status=status.HTTP_400_BAD_REQUEST)

        if room.max_occupancy < request.data.get('guests', 1):
            return Response({'error': 'Maximum occupancy exceeded for this room.'}, status=status.HTTP_400_BAD_REQUEST)

        if is_reserved(room=room,check_in_date=check_in_date, check_out_date=check_out_date):
            return Response({'error': 'Room already reserved for this date range.'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.data["room"] = room.pk

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Reservation made: {serializer.data}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReservationCancelView(generics.DestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        reservation_id = kwargs.get('pk')
        reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)

        if reservation.status != 'accepted':
            return Response({'error': 'This reservation cannot be canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        reservation.delete()
        return Response({'message': 'Reservation canceled successfully.'}, status=status.HTTP_204_NO_CONTENT)

class ReservationUpdateView(generics.UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]