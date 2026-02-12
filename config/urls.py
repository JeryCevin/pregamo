from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # <--- Wajib ada agar Login.html jalan
from django.conf import settings               # <--- Wajib untuk media/static
from django.conf.urls.static import static     # <--- Wajib untuk media/static

urlpatterns = [
    # 1. Admin Django
    path('admin/', admin.site.urls),

    # 2. App Users (Login, Logout, Google Auth)
    # Saya ganti 'api/' menjadi 'users/' agar sesuai nama foldernya. 
    # (Pastikan javascript login google Anda menyesuaikan, atau kembalikan ke 'api/' jika malas ubah JS)
    path('users/', include('users.urls')), 

    # 3. App Dashboard (Tampilan Utama)
    path('dashboard/', include('dashboard.urls')),

    # 4. App Prediction (Fitur Prediksi & Riwayat)
    path('api/predict/', include('prediction.urls')),

    # 5. Halaman Utama (Root URL) -> Menampilkan Login.html saat web pertama dibuka
    path('', TemplateView.as_view(template_name='Login.html'), name='home'),
]

# Konfigurasi agar file gambar/media bisa muncul saat mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)