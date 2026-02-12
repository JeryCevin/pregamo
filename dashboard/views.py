# dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Import model dari folder users
from prediction.models import CarModel, Brand

@login_required(login_url='/') # Pastikan user login dulu
def index(request):
    """
    Menampilkan halaman dashboard utama
    """
    total_car = CarModel.objects.count()
    total_brand = Brand.objects.count()
    
    context = {
        'user': request.user,
        'total_mobil': total_car,
        'total_brand': total_brand
    }
    # Pastikan file HTML ada di folder templates/dashboard/dashboard.html
    # Atau sesuaikan nama file HTML Anda
    return render(request, 'dashboard/dashboard.html', context)