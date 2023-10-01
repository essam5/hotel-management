
from django.contrib import admin, messages
from .models import Reservation
from .views import is_reserved

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in_date', 'check_out_date', 'status')
    list_filter = ('check_in_date', 'check_out_date', 'status')


    def save_model(self, request, obj, form, change):
                
        # Check if the room is available for the specified date range    
                
        if not change:
            room = obj.room
            check_in_date = obj.check_in_date
            check_out_date = obj.check_out_date

            if room.availability != 'available':
                messages.error(request, 'Room is not available for reservation.')
                return

            if room.max_occupancy < obj.guests:
                messages.error(request, 'Maximum occupancy exceeded for this room.')
                return

            if  is_reserved(room, check_in_date, check_out_date):
                messages.error(request, 'Room already reserved for this date range.')
                return

        obj.save()
 

admin.site.register(Reservation, ReservationAdmin)