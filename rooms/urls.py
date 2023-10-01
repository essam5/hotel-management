
from django.urls import path
from . import views

urlpatterns = [
    path('', views.RoomListCreateView.as_view(), name='room-list-create'),
    # Room Management endpoints
    path('create/', views.RoomListCreateView.as_view(), name='room-create'),
    path('available/', views.AvailableRoomsListView.as_view(), name='available-rooms-list'),
]
