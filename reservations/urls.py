
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReservationListCreateView.as_view(), name='reservation-list-create'),
    # Reservation Management endpoints
    path('create/', views.ReservationListCreateView.as_view(), name='reservation-create'),
    path('cancel/<int:pk>/', views.ReservationCancelView.as_view(), name='cancel-reservation'),
    path('update/<int:pk>/', views.ReservationUpdateView.as_view(), name='update-reservation'),

]
