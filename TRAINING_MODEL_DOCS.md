# 🚀 Fitur Training Model ML - Dokumentasi

## 📋 Overview
Fitur ini memungkinkan Anda untuk melatih ulang model Machine Learning prediksi harga mobil dengan mudah melalui Admin Panel, lengkap dengan **Data Cleaning Pipeline** untuk memastikan akurasi dan RMSE yang optimal.

---

## ✨ Fitur Utama

### 1. **Data Cleaning Otomatis**
Sebelum training, data akan dibersihkan secara otomatis:
- ✅ **Hapus duplikat** - Data yang sama persis
- ✅ **Hapus missing values** - Data kosong/null
- ✅ **Hapus outliers** - Menggunakan IQR method
- ✅ **Validasi range data**:
  - Tahun: 1990-2026
  - Jarak tempuh: >= 0
  - CC: 500-5000
  - Harga: >= 10 juta
- ✅ **Standardisasi kategorikal**:
  - Transmisi: manual/automatic
  - Bahan bakar: petrol/diesel/hybrid/electric

### 2. **Training Model**
- Algoritma: **Random Forest Regressor**
- Split: 80% training, 20% testing
- Hyperparameters optimal untuk performa terbaik

### 3. **Tracking & Metrics**
Setiap training disimpan dengan detail:
- Total data vs data setelah cleaning
- **RMSE** (Root Mean Square Error)
- **MAE** (Mean Absolute Error)
- **R² Score** (akurasi dalam %)
- Waktu training
- Log lengkap proses
- Error message (jika gagal)

---

## 🎯 Cara Menggunakan

### **Step 1: Pastikan Database Running**
Jika menggunakan MySQL, pastikan MySQL server sudah running:
```bash
# Windows - XAMPP/WAMP
# Atau jalankan MySQL service dari Services

# Cek status
mysql -u root -p -e "SELECT 1"
```

### **Step 2: Jalankan Migrasi Database**
```bash
python manage.py migrate
```

### **Step 3: Akses Admin Panel**
1. Login ke Django Admin: `http://localhost:8000/admin/`
2. Pilih menu **"Riwayat Training Models"**
3. Klik tombol **"🚀 Train Model Baru"** di pojok kanan atas

### **Step 4: Training Model**
1. Pilih **Brand** yang ingin dilatih (Toyota, Honda, dll)
2. Pastikan data tersedia minimal **50 data** setelah cleaning
3. Klik **"🚀 Mulai Training"**
4. Tunggu proses selesai (~30-60 detik)

### **Step 5: Lihat Hasil**
Setelah training selesai:
- ✅ Status berubah menjadi **"Completed"** (hijau)
- ✅ Model baru otomatis tersimpan di `ml_models/{Brand}_Model.pkl`
- ✅ Cache model di-clear otomatis
- ✅ Prediksi selanjutnya akan menggunakan model baru

---

## 📊 Interpretasi Metrics

### **RMSE (Root Mean Square Error)**
- Rata-rata error prediksi dalam Rupiah
- **Semakin kecil semakin baik**
- Contoh: RMSE = 15.000.000 artinya rata-rata prediksi meleset ±15 juta

### **MAE (Mean Absolute Error)**
- Error absolut rata-rata dalam Rupiah
- **Semakin kecil semakin baik**
- Lebih robust terhadap outliers daripada RMSE

### **R² Score**
- Persentase akurasi model (0-1 atau 0%-100%)
- **Semakin tinggi semakin baik**
- Contoh: R² = 0.85 = 85% akurat

**Interpretasi R² Score:**
- **> 0.9 (90%)** = Excellent! 🎉
- **0.8 - 0.9 (80-90%)** = Very Good ✅
- **0.7 - 0.8 (70-80%)** = Good 👍
- **0.6 - 0.7 (60-70%)** = Fair ⚠️
- **< 0.6 (< 60%)** = Poor - Perlu lebih banyak data 📉

---

## ⚠️ Troubleshooting

### **❌ Error: "Data terlalu sedikit setelah cleaning"**
**Penyebab:** Data bersih < 50 rows setelah cleaning

**Solusi:**
1. Tambahkan lebih banyak data di **Manage Datasets**
2. Import data dari Excel/CSV
3. Pastikan data berkualitas (tidak banyak outliers/duplikat)

### **❌ Error: "Can't connect to database"**
**Penyebab:** MySQL/Database server tidak running

**Solusi:**
```bash
# Windows - XAMPP
- Start MySQL dari XAMPP Control Panel

# Windows - WAMP
- Start MySQL dari WAMP

# Atau cek service
services.msc → MySQL → Start
```

### **❌ Error: "Missing required columns"**
**Penyebab:** Data tidak lengkap (ada kolom yang kosong)

**Solusi:**
Pastikan setiap data memiliki kolom:
- brand
- model
- tahun
- jarak_tempuh
- transmisi
- bahan_bakar
- cc
- harga

### **❌ RMSE/R² Score Buruk**
**Penyebab:** Data tidak representatif atau terlalu sedikit

**Solusi:**
1. ✅ Tambahkan lebih banyak data (minimal 100-200 data per brand)
2. ✅ Pastikan data mencakup berbagai model, tahun, harga
3. ✅ Hindari data yang bias (hanya 1-2 model saja)
4. ✅ Cek kualitas data di **Manage Datasets**

---

## 🔄 Best Practices

### **Kapan Harus Retrain Model?**
1. ✅ **Setelah import data baru** (>10% data bertambah)
2. ✅ **Performa prediksi menurun** (banyak prediksi tidak akurat)
3. ✅ **Data harga di pasaran berubah signifikan**
4. ✅ **Menambah model mobil baru**
5. ✅ **Setiap bulan** (untuk data yang dinamis)

### **Tips untuk Model yang Lebih Baik:**
1. 📊 **Minimal 100-200 data per brand** untuk hasil optimal
2. 🎯 **Data harus bervariasi**:
   - Berbagai model mobil
   - Berbagai tahun (jangan hanya 2023-2024)
   - Berbagai range harga
   - Berbagai jarak tempuh
3. 🧹 **Data harus berkualitas**:
   - Harga real/market price
   - Jarak tempuh akurat
   - Tidak ada data palsu/asal
4. 🔄 **Retrain secara berkala** (tidak perlu terlalu sering)

### **Perbandingan Sebelum dan Sesudah Training:**
Setelah training, bandingkan metrics:
```
Model Lama:
- RMSE: 25,000,000
- R²: 0.75 (75%)

Model Baru (setelah cleaning + retrain):
- RMSE: 15,000,000 ✅ (Lebih baik!)
- R²: 0.87 (87%) ✅ (Lebih akurat!)
```

---

## 📁 File Structure

```
Project-Skripsi/
├── ml_models/                    # Model ML tersimpan di sini
│   ├── Toyota_Model.pkl
│   ├── Honda_Model.pkl
│   └── ...
├── prediction/
│   ├── models.py                 # Model TrainingHistory
│   ├── training.py               # Logic training & cleaning
│   ├── admin.py                  # Admin interface
│   └── logika_ml.py              # Logic prediksi
└── templates/
    └── admin/
        └── prediction/
            └── train_model.html  # Form training
```

---

## 🛠️ Technical Details

### **Data Cleaning Pipeline:**
```python
1. Load data dari CarDataset
2. Remove duplicates
3. Remove missing values
4. Remove outliers (IQR method)
5. Validate ranges
6. Standardize categoricals
7. Filter invalid categories
8. Return cleaned data + stats
```

### **Model Training Pipeline:**
```python
1. Prepare features (encoding)
2. Split data (80/20)
3. Train RandomForestRegressor
4. Evaluate on test set
5. Save model to ml_models/
6. Clear cache
7. Save metrics to database
```

---

## 📞 Support

Jika ada pertanyaan atau kendala:
1. Cek **Riwayat Training Models** → kolom **Error Message**
2. Lihat **Log Pesan** untuk detail proses
3. Pastikan semua dependencies terinstall: `pip install -r requirements.txt`

---

**Happy Training! 🚀**
