from django.urls import path
from . import views

urlpatterns = [
    # Halaman Utama Dashboard
    path('', views.index, name='dashboard'),
]