# prediction/logika_ml.py
"""
Modul khusus untuk menangani logika Machine Learning.
Berisi fungsi pemuatan model, pemrosesan data, dan prediksi harga mobil.
"""

import os
import pickle
import pandas as pd
from django.conf import settings

# Cache ML models untuk performa lebih baik
_ml_models_cache = {}

def hitung_estimasi_harga(brand, model_name, year, mileage, transmission, fuel, engine_cc):
    """
    Menghitung estimasi harga mobil menggunakan model Machine Learning.
    
    Args:
        brand (str): Nama brand mobil (Toyota, Honda, dll)
        model_name (str): Nama model mobil
        year (int): Tahun produksi
        mileage (int): Jarak tempuh dalam kilometer
        transmission (str): Jenis transmisi (Manual/Automatic)
        fuel (str): Jenis bahan bakar (Petrol/Diesel/Hybrid)
        engine_cc (int): Kapasitas mesin dalam CC
    
    Returns:
        int: Harga prediksi dalam rupiah
    
    Raises:
        FileNotFoundError: Jika file model tidak ditemukan
        ValueError: Jika data input tidak valid
        Exception: Untuk error umum lainnya
    """
    try:
        # 1. Persiapan data input sebagai DataFrame
        # PENTING: Nama kolom harus SAMA PERSIS dengan yang digunakan saat training model
        final_features = pd.DataFrame({
            'year': [year],
            'mileage': [mileage],
            'engineSize': [engine_cc],
            'model': [model_name],
            'transmission': [transmission],
            'fuelType': [fuel]
        })
        
        print(f"[ML] Input features: {final_features.to_dict('records')[0]}")
        
        # 2. Load Model PKL dengan caching
        brand_key = brand.lower()
        
        # Mapping nama brand ke nama file model
        model_file_mapping = {
            'toyota': 'Toyota_Model.pkl',
            'honda': 'Honda_Model.pkl',
            'mitsubishi': 'Mitsubishi_Model.pkl',
            'suzuki': 'Suzuki_Model.pkl',
            'daihatsu': 'Daihatsu_Model.pkl'
        }
        
        # Cek apakah model sudah ada di cache
        if brand_key not in _ml_models_cache:
            model_filename = model_file_mapping.get(brand_key)
            
            if not model_filename:
                raise ValueError(f'Model untuk brand "{brand}" tidak tersedia')
            
            model_path = os.path.join(settings.BASE_DIR, 'ml_models', model_filename)
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f'File model {model_filename} tidak ditemukan di {model_path}')
            
            # Load model dan simpan ke cache
            print(f"[ML] Loading model: {model_filename}")
            with open(model_path, 'rb') as file:
                _ml_models_cache[brand_key] = pickle.load(file)
            print(f"[ML] Model {brand} berhasil dimuat dan di-cache")
        else:
            print(f"[ML] Menggunakan cached model untuk {brand}")
        
        model = _ml_models_cache[brand_key]
        
        # 3. Prediksi
        prediction = model.predict(final_features)
        harga_hasil = round(prediction[0])
        
        print(f"[ML] Hasil prediksi untuk {brand} {model_name} ({year}): Rp {harga_hasil:,}")
        
        # 4. Validasi hasil prediksi
        if harga_hasil < 0:
            raise ValueError('Hasil prediksi menghasilkan nilai negatif')
        
        return int(harga_hasil)
        
    except FileNotFoundError as e:
        print(f"[ML ERROR] File tidak ditemukan: {e}")
        raise
    except ValueError as e:
        print(f"[ML ERROR] Validasi error: {e}")
        raise
    except Exception as e:
        print(f"[ML ERROR] Unexpected error: {type(e).__name__} - {e}")
        raise Exception(f'Gagal melakukan prediksi: {str(e)}')
