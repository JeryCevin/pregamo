# prediction/views.py
import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Import model dari folder users
from .models import Brand, CarModel

# Import fungsi ML dari modul terpisah
from .logika_ml import hitung_estimasi_harga

# --- HALAMAN FORM PREDIKSI ---
@login_required
def predict_page_view(request):
    all_brands = Brand.objects.prefetch_related('models').all()
    tahun_sekarang = datetime.date.today().year
    list_tahun = list(range(tahun_sekarang, 2011, -1))
    kapasitas_mesin = [1000, 1200, 1300, 1400,1500, 1800, 2000, 2400, 2500]
    total_car = CarModel.objects.count()
    total_brand = Brand.objects.count()
    
    context = {
        'brands': all_brands,
        'user': request.user, 
        'tahun_pilihan': list_tahun,
        'kapasitas_mesins': kapasitas_mesin,
        'total_mobil': total_car,
        'total_brand': total_brand
    }
    return render(request, 'dashboard/dashboard.html', context)

# --- LOGIKA EKSEKUSI PREDIKSI ---
@csrf_exempt
def run_prediction(request):
    print("=== DEBUG: run_prediction dipanggil ===")
    print(f"Method: {request.method}")
    print(f"POST data: {request.POST}")
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Hanya metode POST yang diizinkan'}, status=405)

    try:
        # 1. Ambil data dengan validasi
        data = request.POST
        brand = data.get('brand', '').strip()
        model_name = data.get('model', '').strip()
        transmission = data.get('transmission', '').strip()
        fuel = data.get('fuel', '').strip()
        
        # Cek field kosong
        if not all([brand, model_name, transmission, fuel]):
            return JsonResponse({'error': 'Semua field harus diisi'}, status=400)
        
        # Konversi angka dengan validasi
        try:
            year = int(data.get('year'))
            mileage = int(data.get('mileage'))
            engine_cc = int(data.get('cc'))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Format angka tidak valid'}, status=400)
        
        # Validasi range nilai
        current_year = datetime.date.today().year
        if not (2012 <= year <= current_year):
            return JsonResponse({'error': f'Tahun harus antara 2012-{current_year}'}, status=400)
        if mileage < 1000 or mileage > 300000:
            return JsonResponse({'error': 'Kilometer tidak valid (1.000-300.000)'}, status=400)
        if engine_cc < 100 or engine_cc > 10000:
            return JsonResponse({'error': 'CC mesin tidak valid (100-10.000)'}, status=400)

        # 2. Panggil fungsi Machine Learning untuk prediksi
        harga_hasil = hitung_estimasi_harga(
            brand=brand,
            model_name=model_name,
            year=year,
            mileage=mileage,
            transmission=transmission,
            fuel=fuel,
            engine_cc=engine_cc
        )
        # =====================================================================
        # 3. PENENTUAN RENTANG HARGA BERDASARKAN RMSE
        # =====================================================================
        # PR KAMU: Ganti angka-angka ini dengan nilai RMSE asli dari hasil training modelmu!
        rmse_dict = {
            'Toyota': 33400000,    # Contoh: RMSE Toyota adalah 18.5 Juta
            'Honda': 37000000,     # Contoh: RMSE Honda adalah 15.2 Juta
            'Daihatsu': 16000000,
            'Suzuki': 18400000,
            'Mitsubishi': 36500000
            # Tambahkan merek lain jika ada
        }

        # Ambil RMSE sesuai brand yang diprediksi. 
        # Jika brand tidak ada di dictionary, gunakan nilai default (misal 15 juta)
        rmse_model = rmse_dict.get(brand, 15000000)

        # Hitung Batas Bawah dan Batas Atas
        harga_min = harga_hasil - rmse_model
        harga_max = harga_hasil + rmse_model
        # =====================================================================

        # 4. Kirim hasil lengkap ke Frontend (JavaScript)
        return JsonResponse({
            'harga_prediksi': harga_hasil,
            'harga_min': harga_min,    # Dikirim untuk dirender di modal
            'harga_max': harga_max     # Dikirim untuk dirender di modal
        })

    except ValueError as e:
        # Error dari validasi atau dari fungsi ML
        return JsonResponse({'error': f'Data tidak valid: {str(e)}'}, status=400)
    except FileNotFoundError as e:
        # Error jika file model .pkl tidak ditemukan
        return JsonResponse({'error': 'Model prediksi tidak ditemukan'}, status=404)
    except Exception as e:
        # Error umum lainnya
        print(f"ERROR di run_prediction: {type(e).__name__} - {e}")
        return JsonResponse({'error': f'Terjadi kesalahan: {str(e)}'}, status=500)