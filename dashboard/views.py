# dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Import model dari folder users
from prediction.models import CarModel, Brand
import datetime

@login_required(login_url='/') # Pastikan user login dulu
def index(request):
    """
    Menampilkan halaman utama prediksi
    """
    all_brands = Brand.objects.prefetch_related('models').all()
    total_car = CarModel.objects.count()
    total_brand = Brand.objects.count()
    tahun_sekarang = datetime.date.today().year
    list_tahun = list(range(tahun_sekarang, 2011, -1))
    kapasitas_mesin = [1000, 1200, 1300, 1400,1500, 1800, 2000, 2400, 2500]

    
    context = {
        'user': request.user,
        'total_mobil': total_car,
        'total_brand': total_brand,
        'brands': all_brands,
        'tahun_pilihan': list_tahun,
        'kapasitas_mesins': kapasitas_mesin,
    }
    return render(request, 'dashboard/dashboard.html', context)