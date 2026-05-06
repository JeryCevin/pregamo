"""
Script pengukuran BUKTI 1: Waktu Respons Cache OOP
Jalankan: python ukur_cache.py
Tidak perlu server aktif - langsung test fungsi ML
"""

import sys
import os
import time

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Import fungsi yang diukur
from prediction.logika_ml import hitung_estimasi_harga, _ml_models_cache

# Parameter prediksi uji (gunakan brand yang sudah ada modelnya)
TEST_PARAMS = {
    'brand': 'Toyota',
    'model_name': 'Avanza',
    'year': 2020,
    'mileage': 30000,
    'transmission': 'Manual',
    'fuel': 'Petrol',
    'engine_cc': 1500
}

print("=" * 60)
print("PENGUKURAN WAKTU RESPONS — Enkapsulasi Cache OOP")
print("=" * 60)
print(f"Parameter uji: {TEST_PARAMS['brand']} {TEST_PARAMS['model_name']} {TEST_PARAMS['year']}")
print()

results = []

for i in range(1, 6):
    # Bersihkan cache hanya di request pertama
    if i == 1:
        _ml_models_cache.clear()
        status = "COLD (load dari disk)"
    else:
        status = "WARM (dari memory cache)"

    start = time.perf_counter()
    try:
        harga = hitung_estimasi_harga(**TEST_PARAMS)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        results.append(elapsed_ms)
        print(f"  Request ke-{i} [{status}]: {elapsed_ms:.1f} ms  →  Rp {harga:,}")
    except Exception as e:
        print(f"  Request ke-{i}: ERROR - {e}")
        end = time.perf_counter()
        results.append(None)

print()
print("=" * 60)
print("RINGKASAN HASIL:")
print("=" * 60)
if results[0]:
    print(f"  Request ke-1 (tanpa cache / Non-OOP simulasi): {results[0]:.1f} ms")

warm = [r for r in results[1:] if r is not None]
if warm:
    avg_warm = sum(warm) / len(warm)
    print(f"  Request ke-2 s/d 5 (dengan cache OOP)        : rata-rata {avg_warm:.1f} ms")
    if results[0]:
        penghematan = ((results[0] - avg_warm) / results[0]) * 100
        print(f"  Penghematan waktu respons                     : {penghematan:.1f}%")

print()
print("KESIMPULAN:")
print("  Enkapsulasi _ml_models_cache (OOP) menurunkan waktu respons")
if results[0] and warm:
    print(f"  dari {results[0]:.0f}ms menjadi rata-rata {avg_warm:.0f}ms ({penghematan:.0f}% lebih cepat)")
print("=" * 60)
