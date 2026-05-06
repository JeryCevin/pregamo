from django.urls import path
from . import views 

urlpatterns = [
    # Halaman Tampilan Form
    path('', views.predict_page_view, name='predict_page'),
    
    # Logika Hitung Prediksi (AJAX/Post)
    path('run/', views.run_prediction, name='run_prediction'),
]