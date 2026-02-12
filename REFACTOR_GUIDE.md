# 🚀 REFACTOR COMPLETE - File-Based Training Pipeline

## ✨ Perubahan Besar

Aplikasi sudah di-**refactor** dari model per-row menjadi **file-based pipeline** yang jauh lebih efisien dan user-friendly!

---

## 📋 Apa yang Berubah?

### **SEBELUM (Old):**
- ❌ Input data per-row (satu-satu) → lambat dan ribet
- ❌ Random Forest + data cleaning kompleks → overkill untuk skripsi
- ❌ Admin interface kaku

### **SEKARANG (New):**
- ✅ **Upload file Excel** sekali jadi → cepat!
- ✅ **Linear Regression** sederhana → cocok untuk skripsi
- ✅ **Pipeline visual** yang jelas di admin panel
- ✅ Preprocessing otomatis (mapping transmisi & bahan bakar)

---

## 🎯 Cara Menggunakan Sistem Baru

### **1. Upload Dataset (File Excel)**

1. Login ke Django Admin: `http://localhost:8000/admin/`
2. Pilih menu **"📁 Manage Datasets (Upload File)"**
3. Klik **"Add Dataset File"**
4. Isi form:
   - **Brand:** Pilih brand (Toyota, Honda, dll)
   - **File Excel:** Upload file `.xlsx` dengan kolom:
     ```
     tahun | jarak_tempuh | transmisi | bahan_bakar | harga
     ─────────────────────────────────────────────────────
     2020  | 50000       | Manual    | Bensin      | 250000000
     2021  | 30000       | Matic     | Diesel      | 300000000
     ...
     ```
   - **Deskripsi:** (Opsional) catatan tentang dataset
5. Klik **"Save"**

📊 **Sistem otomatis menghitung:**
- Ukuran file (KB/MB)
- Jumlah baris data

---

### **2. Training Model**

#### **Cara 1: Dari List Dataset**
1. Di halaman **"📁 Manage Datasets"**
2. Klik tombol **"🚀 Train Model"** di sebelah kanan dataset yang dipilih

#### **Cara 2: Dari Halaman Training Khusus**
1. Akses URL: `http://localhost:8000/admin/prediction/file-train-model/`
2. Atau dari menu dataset → Klik link **"Train Model"**
3. **Pilih dataset** dari dropdown
4. Klik tombol besar **"🚀 TRAIN DATA SEKARANG"**
5. Konfirmasi → Tunggu ~10-30 detik
6. ✅ **Selesai!** Model tersimpan di `ml_models/<Brand>_Model.pkl`

---

### **3. Lihat Hasil Training**

1. Pilih menu **"Riwayat Training Models"**
2. Lihat history training dengan detail:
   - ✅ Status (Completed/Failed)
   - ✅ Metrics: **RMSE, MAE, R² Score**
   - ✅ Jumlah data yang digunakan
   - ✅ Waktu training (detik)
   - ✅ Log lengkap proses

---

## 🧹 Preprocessing Otomatis

Sistem otomatis melakukan preprocessing:

### **1. Mapping Transmisi:**
```
'Manual'    → 0
'manual'    → 0
'MT'        → 0
'Matic'     → 1
'matic'     → 1
'Automatic' → 1
'AT'        → 1
```

### **2. Mapping Bahan Bakar:**
```
'Bensin'   → 1
'bensin'   → 1
'Petrol'   → 1
'Diesel'   → 0
'diesel'   → 0
'Solar'    → 0
```

### **3. Data Cleaning:**
- ✅ Drop baris kosong (`dropna()`)
- ✅ Drop baris yang gagal di-mapping
- ✅ Validasi minimal 10 baris data

---

## 🤖 Model ML

### **Algoritma: Linear Regression**
```python
Features (X):
- tahun
- jarak_tempuh
- transmisi (0/1)
- bahan_bakar (0/1)

Target (y):
- harga
```

### **Training Process:**
1. ✅ Load Excel → pandas DataFrame
2. ✅ Preprocessing (mapping + cleaning)
3. ✅ Split 80% train, 20% test
4. ✅ Train Linear Regression
5. ✅ Evaluasi (RMSE, MAE, R²)
6. ✅ Save model ke `ml_models/<Brand>_Model.pkl` (overwrite)

---

## 📊 Interpretasi Metrics

### **RMSE (Root Mean Square Error)**
- Error rata-rata dalam Rupiah
- **Semakin kecil semakin baik**
- Contoh: RMSE = 20.000.000 → rata-rata error ±20 juta

### **MAE (Mean Absolute Error)**
- Error absolut rata-rata
- **Semakin kecil semakin baik**

### **R² Score (Akurasi)**
- 0.0 - 1.0 atau 0% - 100%
- **Semakin tinggi semakin baik**
- **> 0.7 (70%) = Good** untuk Linear Regression
- **> 0.8 (80%) = Very Good**

---

## 📁 Struktur File Baru

```
Project-Skripsi/
├── ml_models/                         # Model tersimpan di sini
│   ├── Toyota_Model.pkl
│   ├── Honda_Model.pkl
│   └── ...
├── media/
│   └── datasets/                      # File Excel upload tersimpan di sini
│       ├── Toyota_dataset_2024.xlsx
│       └── ...
├── prediction/
│   ├── models.py                      # + FileDataset model
│   ├── training_linear.py             # NEW: Linear Regression training
│   ├── training.py                    # OLD: Random Forest (legacy)
│   ├── admin.py                       # + FileDatasetAdmin
│   └── logika_ml.py                   # (Tetap sama untuk prediksi)
└── templates/
    └── admin/
        └── prediction/
            └── train_model_linear.html # NEW: Halaman training visual
```

---

## ⚡ Keunggulan Sistem Baru

1. ✅ **Lebih Cepat:** Upload 1 file vs input ratusan row manual
2. ✅ **Lebih Sederhana:** Linear Regression lebih mudah dijelaskan di skripsi
3. ✅ **Pipeline Visual:** Flow jelas: Upload → Train → Save
4. ✅ **Auto Preprocessing:** Tidak perlu manual cleaning
5. ✅ **File Management:** Dataset terorganisir per brand
6. ✅ **History Tracking:** Bisa lihat semua training history

---

## 🎓 Untuk Skripsi

### **Penjelasan yang Bisa Dipakai:**

**"Sistem prediksi harga mobil bekas ini menggunakan:**
- **Algoritma:** Linear Regression
- **Fitur:** 4 variabel (tahun, jarak_tempuh, transmisi, bahan_bakar)
- **Workflow:** File-based training pipeline
  1. Upload dataset Excel
  2. Preprocessing otomatis (encoding kategorikal)
  3. Training model
  4. Evaluasi dengan RMSE, MAE, R²
  5. Deploy model untuk prediksi real-time

**Keuntungan Linear Regression:**
- Simple & mudah diinterpretasi
- Cepat (training < 30 detik)
- Cocok untuk hubungan linear antara fitur dan harga
- Tidak overfitting seperti model kompleks"

---

## 🔄 Migrasi dari Sistem Lama

Jika Anda punya data lama di `CarDataset`:

1. **Export data ke Excel:**
   - Dari admin → Manage Datasets (Legacy) → Export to Excel
   
2. **Upload ulang via sistem baru:**
   - Manage Datasets (Upload File) → Add → Upload Excel

3. **Train ulang model:**
   - Pilih dataset → Train Model

**Note:** Model lama akan di-overwrite dengan model baru.

---

## 🆘 Troubleshooting

### **Error: "Kolom tidak ditemukan"**
**Solusi:** Pastikan Excel punya kolom:
- `tahun`
- `jarak_tempuh`
- `transmisi`
- `bahan_bakar`
- `harga`

### **Error: "Data terlalu sedikit"**
**Solusi:** Minimal 10 baris data diperlukan setelah preprocessing.

### **RMSE/R² Buruk**
**Solusi:**
- Tambah lebih banyak data (100+ rows)
- Pastikan data berkualitas (harga real)
- Cek data tidak ada outliers ekstrem

---

## 📞 Support

Jika ada pertanyaan:
1. Cek **Riwayat Training Models** → Log Pesan
2. Cek **Error Message** jika training failed

---

**🎉 Selamat! Sistem baru siap digunakan untuk skripsi Anda!**
