from django.urls import path
from . import views  # Import dari folder prediction itu sendiri

urlpatterns = [
    # Halaman Tampilan Form
    path('', views.predict_page_view, name='predict_page'),
    
    # Logika Hitung Prediksi (AJAX/Post)
    path('run/', views.run_prediction, name='run_prediction'),
    
    # Halaman Riwayat
    path('history/', views.history_page, name='predict_history'),
]