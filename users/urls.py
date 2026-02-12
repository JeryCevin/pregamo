# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/google/', views.google_login, name='google_login'),
    path('callback/google/', views.google_callback, name='google_callback'),
    path('logout/', views.google_logout, name='logout'),
]