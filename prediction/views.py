# prediction/views.py
import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Import model dari folder users
from .models import Brand, PredictionHistory

# Import fungsi ML dari modul terpisah
from .logika_ml import hitung_estimasi_harga

# --- HALAMAN FORM PREDIKSI ---
@login_required
def predict_page_view(request):
    all_brands = Brand.objects.prefetch_related('models').all()
    tahun_sekarang = datetime.date.today().year
    list_tahun = list(range(tahun_sekarang, 2011, -1))
    
    context = {
        'brands': all_brands,
        'user': request.user, 
        'tahun_pilihan': list_tahun
    }
    return render(request, 'prediction/predict.html', context)

# --- HALAMAN RIWAYAT ---
@login_required
def history_page(request):
    user_history = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'riwayat': user_history,
        'user': request.user
    }
    return render(request, 'prediction/history.html', context)

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
        if mileage < 0 or mileage > 1000000:
            return JsonResponse({'error': 'Kilometer tidak valid (0-1.000.000)'}, status=400)
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

        # 3. Simpan ke Database
        if request.user.is_authenticated:
            PredictionHistory.objects.create(
                user=request.user,
                brand=brand,
                model_name=model_name,
                year=year,
                mileage=mileage,
                transmission=transmission,
                fuel=fuel,
                engine_cc=engine_cc,
                predicted_price=harga_hasil
            )

        return JsonResponse({'harga_prediksi': harga_hasil})

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