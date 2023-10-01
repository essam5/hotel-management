from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room


class Reservation(models.Model):
    
    status_TYPE_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=status_TYPE_CHOICES, default='pending')
    guests = models.PositiveIntegerField(default=1)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Reservation for {self.user.username} - Room {self.room.room_number}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Check if the reservation has been accepted
        if self.status == 'accepted':
            self.room.availability = 'reserved'
            self.room.save()