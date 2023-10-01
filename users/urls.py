
from django.urls import path
from . import views

urlpatterns = [
    # User Management endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
]
