
from rest_framework import serializers
from .models import  Reservation

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('id', 'user', 'room', 'check_in_date', 'check_out_date', 'status')

    def __init__(self, *args, **kwargs):
        super(ReservationSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user and request.user.is_staff:
            self.fields['status'].read_only = False
            self.fields['status'].validators = []
        else:
            self.fields['status'].read_only = True

        if not (request and request.user and request.user.is_staff):
            self.fields.pop('status')
