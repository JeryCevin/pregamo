from django.urls import path
from . import views

urlpatterns = [
    # Halaman Utama Dashboard
    # name='dashboard_home' ini PENTING karena dipanggil saat redirect setelah login
    path('', views.index, name='dashboard'),
]